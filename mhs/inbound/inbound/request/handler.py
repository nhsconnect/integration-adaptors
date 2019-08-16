"""This module defines the inbound request handler component."""

from utilities import integration_adaptors_logger as log
from typing import Dict, Callable
import tornado.web

from mhs_common.state import persistence_adaptor as pa
from mhs_common.state import work_description as wd
from mhs_common.state.persistence_adaptor import PersistenceAdaptor
import mhs_common.messages.ebxml_ack_envelope as ebxml_ack_envelope
import mhs_common.messages.ebxml_envelope as ebxml_envelope
import mhs_common.messages.ebxml_request_envelope as ebxml_request_envelope
from utilities import message_utilities
import mhs_common.workflow as workflow
from utilities.timing import time_request

logger = log.IntegrationAdaptorsLogger('INBOUND_HANDLER')


class InboundHandler(tornado.web.RequestHandler):
    """A Tornado request handler intended to handle incoming HTTP requests from a remote MHS."""
    state_store: PersistenceAdaptor
    party_id: str
    workflows: Dict[str, workflow.CommonWorkflow]

    def initialize(self, workflows: Dict[str, workflow.CommonWorkflow],
                   state_store: pa.PersistenceAdaptor, party_id: str):
        """Initialise this request handler with the provided dependencies.
        :param workflows:
        :param state_store: The state store
        :param party_id: The party ID of this MHS. Sent in ebXML acknowledgements.
        """
        self.workflows = workflows
        self.party_id = party_id
        self.state_store = state_store

    @time_request
    async def post(self):
        logger.info('001', 'Inbound POST received: {request}', {'request': self.request})

        try:
            request_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(self.request.headers,
                                                                                      self.request.body.decode())
        except ebxml_envelope.EbXmlParsingError as e:
            logger.error('020', 'Failed to parse response: {exception}', {'exception': e})
            raise tornado.web.HTTPError(500, 'Error occurred during message parsing',
                                        reason=f'Exception during inbound message parsing {e}') from e

        ref_to_message_id = self.extract_ref_message(request_message)
        self._extract_correlation_id(request_message)
        self._extract_message_id(request_message)

        try:
            work_description = await wd.get_work_description_from_store(self.state_store, ref_to_message_id)
        except wd.EmptyWorkDescriptionError as e:
            logger.warning('003', 'No work description found in state store with {messageId}',
                           {'messageId': ref_to_message_id})
            raise tornado.web.HTTPError(500, 'No work description in state store, unsolicited message '
                                             'received from spine',
                                        reason="Unknown message reference") from e

        message_workflow = self.workflows[work_description.workflow]
        logger.info('004', 'Retrieved work description from state store, forwarding message to {workflow}',
                    {'workflow': message_workflow})
        received_message = request_message.message_dictionary[ebxml_request_envelope.MESSAGE]
        try:
            await message_workflow.handle_inbound_message(work_description, received_message)
            self._send_ack(request_message)
        except Exception as e:
            logger.error('005', 'Exception in workflow {e}', {'e': e})
            raise tornado.web.HTTPError(500, 'Error occurred during message processing,'
                                             ' failed to complete workflow',
                                        reason=f'Exception in workflow') from e

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
        correlation_id = message.message_dictionary[ebxml_envelope.CONVERSATION_ID]
        log.correlation_id.set(correlation_id)
        logger.info('007', 'Set correlation id from inbound request.')

    def _extract_message_id(self, message):
        """
        Extracts the message id of the inbound message, this is to be logg
        :param message:
        :return:
        """
        message_id = message.message_dictionary[ebxml_envelope.MESSAGE_ID]
        log.inbound_message_id.set(message_id)
        logger.info('009', 'Found inbound message id on request.')

    def extract_ref_message(self, message):
        """
        Extracts the reference-to message id and assigns it as the message Id in logging
        :param message:
        :return: the message id the inbound message is a response to
        """
        message_id = message.message_dictionary[ebxml_envelope.RECEIVED_MESSAGE_ID]
        log.message_id.set(message_id)
        logger.info('010', 'Found message id on inbound message.')
        return message_id
