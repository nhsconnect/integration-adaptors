"""This module defines the inbound request handler component."""

from typing import Dict, Optional

import mhs_common.messages.common_ack_envelope as common_ack_envelope
import mhs_common.messages.ebxml_ack_envelope as ebxml_ack_envelope
import mhs_common.messages.ebxml_envelope as ebxml_envelope
import mhs_common.messages.ebxml_nack_envelope as ebxml_nack_envelope
import mhs_common.messages.ebxml_request_envelope as ebxml_request_envelope
import mhs_common.workflow as workflow
import tornado.web

from mhs_common.workflow.common import MessageData
from utilities import mdc
from mhs_common.configuration import configuration_manager
from mhs_common.handler import base_handler
from mhs_common.messages.envelope import CONVERSATION_ID, MESSAGE_ID, RECEIVED_MESSAGE_ID
from persistence import persistence_adaptor as pa
from mhs_common.state import work_description as wd
from persistence.persistence_adaptor import PersistenceAdaptor
from mhs_common.workflow import asynchronous_forward_reliable as forward_reliable
from utilities import integration_adaptors_logger as log
from utilities.timing import time_request
import logging

logger = log.IntegrationAdaptorsLogger(__name__)


class InboundHandler(base_handler.BaseHandler):
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
        super().initialize(workflows, config_manager)
        self.party_id = party_id
        self.work_description_store = work_description_store

    @time_request
    async def post(self):
        logger.info('Inbound POST received: {request}', fparams={'request': self.request})
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Request body: %s', self.request.body.decode() if self.request.body else None)
        request_message = self._extract_incoming_ebxml_request_message()

        message_id = self._extract_message_id(request_message)
        interaction_id = self._extract_interaction_id(request_message)
        ref_to_message_id = self._extract_ref_message(request_message)
        correlation_id = self._extract_correlation_id(request_message)

        if not self._is_message_intended_for_receiving_mhs(request_message):
            logger.info("Skipping message as it was not intended for this recipient")
            self._return_message_to_message_initiator(request_message)
            return

        ebxml = request_message.message_dictionary[ebxml_request_envelope.EBXML]
        payload = request_message.message_dictionary[ebxml_request_envelope.MESSAGE]
        attachments = request_message.message_dictionary[ebxml_request_envelope.ATTACHMENTS]

        message_data = MessageData(ebxml, payload, attachments)

        if ref_to_message_id:
            logger.info(f'RefToMessageId on inbound reply: handling as an referenced reply message')
            await self._handle_referenced_reply_message(ref_to_message_id, correlation_id, message_data)
        else:
            logger.info(f'No RefToMessageId on inbound reply: handling as an unsolicited message')
            await self._handle_unsolicited_message(message_id, correlation_id, interaction_id, message_data)
        self._send_ack(request_message)

    async def _handle_referenced_reply_message(self, message_id: str, correlation_id: str, message_data: MessageData):
        work_description = await self._get_work_description_from_store(message_id)
        message_workflow = self.workflows[work_description.workflow]
        logger.info('Forwarding message {message_id} to {workflow}', fparams={'workflow': message_workflow, 'message_id': message_id})

        try:
            await message_workflow.handle_inbound_message(message_id, correlation_id, work_description, message_data)
        except Exception as e:
            logger.exception('Exception in workflow')
            raise tornado.web.HTTPError(500, 'Error occurred during message processing, failed to complete workflow',
                                        reason=f'Exception in workflow') from e

    async def _get_work_description_from_store(self, message_id: str):
        work_description = await wd.get_work_description_from_store(self.work_description_store, message_id)
        if work_description:
            logger.info(f'Retrieved work description for message {message_id} from state store')
            return work_description
        else:
            logger.error(f'No work description found in state store for message {message_id}')
            raise tornado.web.HTTPError(500, f'Unknown message reference {message_id}',
                                        reason="Unknown message reference")

    async def _handle_unsolicited_message(self, message_id: str, correlation_id: str,
                                          interaction_id: str, message_data: MessageData):
        # Lookup workflow for request
        interaction_details = self._get_interaction_details(interaction_id)
        message_workflow = self._extract_default_workflow(interaction_details, interaction_id)

        # If it matches forward reliable workflow, then this will be an unsolicited request from another GP system.
        # So let the workflow handle this.
        if isinstance(message_workflow, forward_reliable.AsynchronousForwardReliableWorkflow):
            await self.handle_forward_reliable_unsolicited_request(message_id, correlation_id, message_workflow, message_data)
        # If not, then something has gone wrong
        else:
            logger.error('Received unsolicited message for a workflow {workflow} that does not support unsolicited messaging',
                         fparams={'workflow': interaction_details['workflow']})
            raise tornado.web.HTTPError(500, 'Unsolicited messaging is not supported for this interaction type',
                                        reason="Unsolicited messaging not supported for this interaction")

    async def handle_forward_reliable_unsolicited_request(self, message_id: str, correlation_id: str,
                                                          forward_reliable_workflow: workflow.AsynchronousForwardReliableWorkflow,
                                                          message_data: MessageData):
        logger.info('Received unsolicited inbound request for the forward-reliable workflow. Passing the '
                    'request to forward-reliable workflow.')
        try:
            await forward_reliable_workflow.handle_unsolicited_inbound_message(message_id, correlation_id, message_data)
        except Exception as e:
            logger.exception('Exception in workflow')
            raise tornado.web.HTTPError(500, 'Error occurred during message processing, failed to complete workflow',
                                        reason=f'Exception in workflow') from e

    def _send_ack(self, parsed_message: ebxml_envelope.EbxmlEnvelope):
        logger.info('Building and sending acknowledgement')
        self._send_ebxml_message(parsed_message, is_positive_ack=True, additional_context={})

    def _send_nack(self, request_message: ebxml_envelope.EbxmlEnvelope, nack_context):
        logger.info('Building and sending negative acknowledgement')
        self._send_ebxml_message(request_message, is_positive_ack=False, additional_context=nack_context)

    def _send_ebxml_message(self, parsed_message, is_positive_ack, additional_context):
        message_details = parsed_message.message_dictionary

        base_context = {
            ebxml_envelope.FROM_PARTY_ID: self.party_id,
            ebxml_envelope.TO_PARTY_ID: message_details[ebxml_envelope.FROM_PARTY_ID],
            ebxml_envelope.CPA_ID: message_details[ebxml_envelope.CPA_ID],
            ebxml_envelope.CONVERSATION_ID: message_details[ebxml_envelope.CONVERSATION_ID],
            common_ack_envelope.RECEIVED_MESSAGE_TIMESTAMP: message_details[ebxml_envelope.TIMESTAMP],
            ebxml_envelope.RECEIVED_MESSAGE_ID: message_details[ebxml_envelope.MESSAGE_ID]
        }

        base_context.update(additional_context)

        if is_positive_ack:
            message = ebxml_ack_envelope.EbxmlAckEnvelope(base_context)
        else:
            message = ebxml_nack_envelope.EbxmlNackEnvelope(base_context)

        message_id, http_headers, serialized_message = message.serialize()
        for k, v in http_headers.items():
            self.set_header(k, v)

        self.write(serialized_message)

    def _extract_correlation_id(self, message):
        correlation_id = message.message_dictionary[CONVERSATION_ID]
        mdc.correlation_id.set(correlation_id)
        logger.info('Set correlation id from inbound request.')
        return correlation_id

    def _extract_message_id(self, message):
        """
        Extracts the message id of the inbound message, this is to be included in the standard log format
        :param message:
        :return: the inbound message id assigned to this message by sender
        """
        message_id = message.message_dictionary[MESSAGE_ID]
        mdc.inbound_message_id.set(message_id)
        logger.info('Found inbound message id on request.')
        return message_id

    def _extract_ref_message(self, message) -> Optional[str]:
        """
        Extracts the reference-to message id and assigns it as the message Id in logging
        :param message:
        :return: the ref-to message id from the inbound reply or None for unsolicited messages
        """
        if RECEIVED_MESSAGE_ID in message.message_dictionary:
            message_id = message.message_dictionary[RECEIVED_MESSAGE_ID]
            mdc.message_id.set(message_id)
            logger.info('Found "reference to" message id on inbound message.')
            return message_id
        logger.info('Inbound message did not contain a "reference to" message id')
        return None


    def _extract_interaction_id(self, message):
        """
        Extracts the interaction id of the inbound message and assigns it as the interaction Id in logging
        :param message:
        :return:
        """
        interaction_id = message.message_dictionary[ebxml_envelope.ACTION]
        mdc.interaction_id.set(interaction_id)
        logger.info("Found interaction id '%s' on inbound message.", interaction_id)
        return interaction_id

    def _extract_incoming_ebxml_request_message(self):
        try:
            request_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(self.request.headers,
                                                                                      self.request.body.decode())
        except ebxml_envelope.EbXmlParsingError as e:
            logger.exception('Failed to parse response')
            raise tornado.web.HTTPError(500, 'Error occurred during message parsing',
                                        reason=f'Exception during inbound message parsing {e}') from e

        return request_message

    def _is_message_intended_for_receiving_mhs(self, request_message):
        """
        Asserts whether the incoming message was intended for this MHS instance given the to party key defined in the
        message.

        error_code, severity and description defined as per the TMS Error Base v3.0 document

        :param request_message: the parsed ebxml request message
        """
        return self.party_id == request_message.message_dictionary[ebxml_envelope.TO_PARTY_ID]

    def _return_message_to_message_initiator(self, request_message):
        try:
            # these values are taken defined as per the TMS Error Base v3.0 document
            nack_context = {
                ebxml_envelope.ERROR_CODE: "ValueNotRecognized",
                ebxml_envelope.DESCRIPTION: "501314:Invalid To Party Type attribute",
                ebxml_envelope.SEVERITY: "Error"
            }
            self._send_nack(request_message, nack_context)
        except Exception as e:
            logger.exception('Exception when sending nack')
            raise tornado.web.HTTPError(500, 'Error occurred during message processing,'
                                             ' failed to complete workflow',
                                        reason=f'Exception in workflow') from e
