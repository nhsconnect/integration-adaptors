"""This module defines the inbound request handler component."""

import logging
from typing import Dict, Callable

import tornado.web

import messages.ebxml_ack_envelope as ebxml_ack_envelope
import messages.ebxml_envelope as ebxml_envelope
import messages.ebxml_request_envelope as ebxml_request_envelope


class InboundHandler(tornado.web.RequestHandler):
    """A Tornado request handler intended to handle incoming HTTP requests from a remote MHS."""

    def initialize(self, callbacks: Dict[str, Callable[[str], None]], party_id: str):
        """Initialise this request handler with the provided dependencies.

        :param callbacks: The dictionary of callbacks to use when a message is received.
        :param party_id: The party ID of this MHS. Sent in ebXML acknowledgements.
        """
        self.callbacks = callbacks
        self.party_id = party_id

    def post(self):
        logging.debug("POST received: %s", self.request)
        logging.debug("Body: %s", self.request.body)

        request_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(self.request.headers,
                                                                                  self.request.body.decode())
        ref_to_id = request_message.message_dictionary[ebxml_envelope.RECEIVED_MESSAGE_ID]
        logging.debug("Message received is in reference to '%s'", ref_to_id)

        if ref_to_id in self.callbacks:
            self._send_ack(request_message)

            received_message = request_message.message_dictionary[ebxml_request_envelope.MESSAGE]
            self.callbacks[ref_to_id](received_message)
        else:
            raise tornado.web.HTTPError(log_message=f"Could not find callback for {ref_to_id}")

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
        _, _, serialized_message = ack_message.serialize()

        self.set_header("Content-Type", "text/xml")
        self.write(serialized_message)
