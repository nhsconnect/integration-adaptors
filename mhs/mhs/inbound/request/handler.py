"""This module defines the inbound request handler component."""

from utilities import integration_adaptors_logger as log
from typing import Dict, Callable
import tornado.web
import mhs.common.messages.ebxml_ack_envelope as ebxml_ack_envelope
import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.ebxml_request_envelope as ebxml_request_envelope
from mhs.common.state import persistence_adaptor as pa
from mhs.common.state import work_description as wd
from mhs.common.state.persistence_adaptor import PersistenceAdaptor
from utilities import message_utilities

logger = log.IntegrationAdaptorsLogger('INBOUND_HANDLER')


class InboundHandler(tornado.web.RequestHandler):
    """A Tornado request handler intended to handle incoming HTTP requests from a remote MHS."""
    state_store: PersistenceAdaptor
    party_id: str

    def initialize(self, state_store: pa.PersistenceAdaptor, party_id: str):
        """Initialise this request handler with the provided dependencies.
        :param state_store: The state store
        :param party_id: The party ID of this MHS. Sent in ebXML acknowledgements.
        """
        self.party_id = party_id
        self.state_store = state_store

    async def post(self):
        logger.info('001', 'Inboound POST recieved: {request}', {'request': self.request})

        request_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(self.request.headers,
                                                                                  self.request.body.decode())
        ref_to_message_id = request_message.message_dictionary[ebxml_envelope.RECEIVED_MESSAGE_ID]

        logger.info('002', 'Message received has reference to {messageID}', {'messageID': ref_to_message_id})

        work_description = None
        try:
            work_description = await wd.get_work_description_from_store(self.state_store, ref_to_message_id)
        except wd.EmptyWorkDescriptionError:
            logger.warning('007', 'No work description found in state store with {messageId}',
                           {'messageId': ref_to_message_id})
            # TODO add unimplemented unsolicited workflow
        workflow = work_description.workflow
        # try:
        #   Workflowlist[workflow].handle_inbound_message(request_message, work_description)
        # except e
        #   raise tornado.web.HTTPError(500, 'Error occurred during message processing, failed to ')

    def _send_ack(self, parsed_message: ebxml_envelope.EbxmlEnvelope):
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
            logger.info('0003', "Didn't receive conversation id from inbound request , so have generated a new one.")
        else:
            log.correlation_id.set(correlation_id)
            logger.info('0004', 'Found correlation id on inbound request.')

    def _extract_message_id(self):
        message_id = self.request.headers.get('Message-Id', None)
        if not message_id:
            message_id = message_utilities.MessageUtilities.get_uuid()
            log.message_id.set(message_id)
            logger.info('0005', "Didn't receive message id in incoming request from supplier, so have generated a new "
                                "one.")
        else:
            log.message_id.set(message_id)
            logger.info('0006', 'Found message id on incoming request.')
        return message_id
