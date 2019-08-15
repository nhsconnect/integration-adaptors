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

    async def post(self):
        logger.info('001', 'Inbound POST recieved: {request}', {'request': self.request})

        request_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(self.request.headers,
                                                                                  self.request.body.decode())
        ref_to_message_id = self.extract_ref_message(request_message)

        logger.info('002', 'Message received has reference to {messageID}', {'messageID': ref_to_message_id})

        try:
            work_description = await wd.get_work_description_from_store(self.state_store, ref_to_message_id)
        except wd.EmptyWorkDescriptionError as e:
            logger.warning('003', 'No work description found in state store with {messageId}',
                           {'messageId': ref_to_message_id})
            raise tornado.web.HTTPError(500, 'No work description in state store, unsolicited message '
                                             'received from spine',
                                        reason="Unknown message reference") from e

        message_workflow = self.workflows[work_description.workflow]
        logger.info('004', 'Retrieved word description from state store, forwarding message to {workflow}',
                    {'workflow': message_workflow})
        received_message = request_message.message_dictionary[ebxml_request_envelope.MESSAGE]
        try:
            await message_workflow.handle_inbound_message(work_description, received_message)
            self._send_ack(request_message)
        except Exception as e:
            logger.error('005', 'Exception in workflow {e}', {'e': e})
            raise tornado.web.HTTPError(500, 'Error occurred during message processing,'
                                             ' failed to complete workflow') from e

    def _send_ack(self, parsed_message: ebxml_envelope.EbxmlEnvelope):
        logger.info('010', 'Building and sending acknowledgement')
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

        self.set_header("Content-Type", "text/xml")
        self.write(serialized_message)

    def _extract_correlation_id(self, message):
        correlation_id = message.message_dictionary[ebxml_envelope.CONVERSATION_ID]
        if not correlation_id:
            correlation_id = message_utilities.MessageUtilities.get_uuid()
            log.correlation_id.set(correlation_id)
            logger.info('006', "Didn't receive conversation id from inbound request , so have generated a new one.")
        else:
            log.correlation_id.set(correlation_id)
            logger.info('007', 'Found correlation id on inbound request.')

    def _extract_message_id(self, message):
        """
        Extracts the message id of the inbound message, this is to be logg
        :param message:
        :return:
        """
        message_id = message.message_dictionary[ebxml_envelope.MESSAGE_ID]
        if not message_id:
            logger.info('008', "Didn't receive message id in inbound message")
        else:
            log.message_id.set(message_id)
            logger.info('009', 'Found inbound message id on request.')
        return message_id

    def extract_ref_message(self, message):
        """
        Extracts the reference-to message id and assigns it as the message Id in logging
        :param message:
        :return: the message id the inbound message is a response to
        """
        try:
            message_id = message.message_dictionary[ebxml_envelope.RECEIVED_MESSAGE_ID]
            log.message_id.set(message_id)
            logger.info('0008', 'Found message id on inbound message.')
            return message_id
        except KeyError:
            logger.info('0007', "No Message reference found ")
            return None
