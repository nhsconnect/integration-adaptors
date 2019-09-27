"""This module defines the inbound request handler component."""

from typing import Dict

import mhs_common.messages.ebxml_ack_envelope as ebxml_ack_envelope
import mhs_common.messages.ebxml_envelope as ebxml_envelope
import mhs_common.messages.ebxml_request_envelope as ebxml_request_envelope
import mhs_common.workflow as workflow
import tornado.web
from mhs_common.configuration import configuration_manager
from mhs_common.messages.envelope import MESSAGE, CONVERSATION_ID, MESSAGE_ID, RECEIVED_MESSAGE_ID, \
    CONTENT_TYPE_HEADER_NAME
from mhs_common.messages.soap_envelope import SoapEnvelope, SoapParsingError
from mhs_common.state import persistence_adaptor as pa
from mhs_common.state import work_description as wd
from mhs_common.state.persistence_adaptor import PersistenceAdaptor
from mhs_common.workflow import forward_reliable
from utilities import integration_adaptors_logger as log
from utilities.timing import time_request

logger = log.IntegrationAdaptorsLogger('INBOUND_HANDLER')


class InboundHandler(tornado.web.RequestHandler):
    """A Tornado request handler intended to handle incoming HTTP requests from a remote MHS."""
    work_description_store: PersistenceAdaptor
    party_id: str
    workflows: Dict[str, workflow.CommonWorkflow]

    def initialize(self, workflows: Dict[str, workflow.CommonWorkflow],
                   config_manager: configuration_manager.ConfigurationManager,
                   work_description_store: pa.PersistenceAdaptor, party_id: str):
        """Initialise this request handler with the provided dependencies.
        :param workflows:
        :param config_manager: The object that can be used to obtain interaction details.
        :param work_description_store: The state store
        :param party_id: The party ID of this MHS. Sent in ebXML acknowledgements.
        """
        self.workflows = workflows
        self.config_manager = config_manager
        self.party_id = party_id
        self.work_description_store = work_description_store

    @time_request
    async def post(self):
        logger.info('001', 'Inbound POST received: {request}', {'request': self.request})

        if self._is_async_request():
            request_message = self._extract_incoming_async_request_message()
        else:
            request_message = self._extract_incoming_sync_request_message()

        ref_to_message_id = self._extract_ref_message(request_message)
        correlation_id = self._extract_correlation_id(request_message)
        self._extract_message_id(request_message)

        received_message = request_message.message_dictionary[MESSAGE]

        try:
            work_description = await wd.get_work_description_from_store(self.work_description_store, ref_to_message_id)
        except wd.EmptyWorkDescriptionError as e:
            await self._handle_no_work_description_found_for_request(e, ref_to_message_id, correlation_id,
                                                                     request_message, received_message)
            return

        message_workflow = self.workflows[work_description.workflow]
        logger.info('004', 'Retrieved work description from state store, forwarding message to {workflow}',
                    {'workflow': message_workflow})

        try:
            await message_workflow.handle_inbound_message(ref_to_message_id, correlation_id, work_description,
                                                          received_message)
            self._send_ack(request_message)
        except Exception as e:
            logger.error('005', 'Exception in workflow {exception}', {'exception': e})
            raise tornado.web.HTTPError(500, 'Error occurred during message processing,'
                                             ' failed to complete workflow',
                                        reason=f'Exception in workflow') from e

    async def _handle_no_work_description_found_for_request(self, e: wd.EmptyWorkDescriptionError,
                                                            ref_to_message_id: str, correlation_id: str,
                                                            request_message:
                                                            ebxml_request_envelope.EbxmlRequestEnvelope,
                                                            received_message: str):
        # Lookup workflow for request
        interaction_id = request_message.message_dictionary[ebxml_envelope.ACTION]
        interaction_details = self.config_manager.get_interaction_details(interaction_id)

        if interaction_details is None:
            logger.error('006', 'Unknown {InteractionId} in request', {'InteractionId': interaction_id})
            raise tornado.web.HTTPError(404, f'Unknown interaction ID: {interaction_id}',
                                        reason=f'Unknown interaction ID: {interaction_id}')

        try:
            workflow = self.workflows[interaction_details['workflow']]
        except KeyError as e:
            logger.error('0008', "Wasn't able to determine workflow for {InteractionId} . This likely is due to a "
                                 "misconfiguration in interactions.json", {"InteractionId": interaction_id})
            raise tornado.web.HTTPError(500,
                                        f"Couldn't determine workflow to invoke for interaction ID: {interaction_id}",
                                        reason=f"Couldn't determine workflow to invoke for interaction ID: "
                                               f"{interaction_id}") from e

        # If it matches forward reliable workflow, then this will be an unsolicited request from another GP system.
        # So let the workflow handle this.
        if isinstance(workflow, forward_reliable.AsynchronousForwardReliableWorkflow):
            logger.info('002', 'Received unsolicited inbound request for the forward-reliable workflow. Passing the '
                               'request to forward-reliable workflow.')
            try:
                await workflow.handle_unsolicited_inbound_message(ref_to_message_id, correlation_id, received_message)
                self._send_ack(request_message)
            except Exception as e:
                logger.error('011', 'Exception in workflow {exception}', {'exception': e})
                raise tornado.web.HTTPError(500, 'Error occurred during message processing,'
                                                 ' failed to complete workflow',
                                            reason=f'Exception in workflow') from e

        # If not, then something has gone wrong
        else:
            logger.warning('003', 'No work description found in state store for message with {workflow} , unsolicited '
                                  'message received unexpectedly from Spine.',
                           {'workflow': interaction_details['workflow']})
            raise tornado.web.HTTPError(500, 'No work description in state store, unsolicited message '
                                             'received from Spine',
                                        reason="Unknown message reference") from e

    def _send_ack(self, parsed_message: ebxml_envelope.EbxmlEnvelope):
        logger.info('012', 'Building and sending acknowledgement')
        message_details = parsed_message.message_dictionary

        ack_context = {
            ebxml_envelope.FROM_PARTY_ID: self.party_id,
            ebxml_envelope.TO_PARTY_ID: message_details[ebxml_envelope.FROM_PARTY_ID],
            ebxml_envelope.CPA_ID: message_details[ebxml_envelope.CPA_ID],
            ebxml_envelope.CONVERSATION_ID: message_details[ebxml_envelope.CONVERSATION_ID],
            ebxml_ack_envelope.RECEIVED_MESSAGE_TIMESTAMP: message_details[ebxml_envelope.TIMESTAMP],
            ebxml_envelope.RECEIVED_MESSAGE_ID: message_details[ebxml_envelope.MESSAGE_ID]
        }

        ack_message = ebxml_ack_envelope.EbxmlAckEnvelope(ack_context)
        message_id, http_headers, serialized_message = ack_message.serialize()
        for k, v in http_headers.items():
            self.set_header(k, v)

        self.write(serialized_message)

    def _extract_correlation_id(self, message):
        correlation_id = message.message_dictionary[CONVERSATION_ID]
        log.correlation_id.set(correlation_id)
        logger.info('007', 'Set correlation id from inbound request.')
        return correlation_id

    def _extract_message_id(self, message):
        """
        Extracts the message id of the inbound message, this is to be logg
        :param message:
        :return:
        """
        message_id = message.message_dictionary[MESSAGE_ID]
        log.inbound_message_id.set(message_id)
        logger.info('009', 'Found inbound message id on request.')

    def _extract_ref_message(self, message):
        """
        Extracts the reference-to message id and assigns it as the message Id in logging
        :param message:
        :return: the message id the inbound message is a response to
        """
        message_id = message.message_dictionary[RECEIVED_MESSAGE_ID]
        log.message_id.set(message_id)
        logger.info('010', 'Found message id on inbound message.')
        return message_id

    def _extract_incoming_async_request_message(self):
        try:
            request_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(self.request.headers,
                                                                                      self.request.body.decode())
        except ebxml_envelope.EbXmlParsingError as e:
            logger.error('020', 'Failed to parse response: {exception}', {'exception': e})
            raise tornado.web.HTTPError(500, 'Error occurred during message parsing',
                                        reason=f'Exception during inbound message parsing {e}') from e

        return request_message

    def _extract_incoming_sync_request_message(self):
        try:
            request_message = SoapEnvelope.from_string(self.request.headers,
                                                                     self.request.body.decode())
        except SoapParsingError as e:
            logger.error('021', 'Failed to parse response: {exception}', {'exception': e})
            raise tornado.web.HTTPError(500, 'Error occurred during message parsing',
                                        reason=f'Exception during inbound message parsing {e}') from e

        return request_message

    def _is_async_request(self):
        return 'multipart/related' in self.request.headers[CONTENT_TYPE_HEADER_NAME]
