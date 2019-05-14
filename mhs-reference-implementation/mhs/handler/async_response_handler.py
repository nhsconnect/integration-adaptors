import logging
from typing import Callable, Dict

from tornado.web import RequestHandler, HTTPError

import mhs.builder.ebxml_ack_message_builder as ack_builder
import mhs.builder.ebxml_message_builder as builder
import mhs.parser.ebxml_message_parser as parser
from mhs.sender.sender import PARTY_ID


class AsyncResponseHandler(RequestHandler):
    """A RequestHandler for asynchronous responses from a remote MHS. Extracts a reference to a previous message from
    messages received and calls the callback registered against this ID."""

    def initialize(self, ack_builder: builder.EbXmlMessageBuilder, message_parser: parser.EbXmlMessageParser,
                   callbacks: Dict[str, Callable[[str], None]]):
        """Initialise this request handler with the provided dependencies.

        :param ack_builder: The message builder to use when building ebXML acknowledgement messages.
        :param message_parser: The message parser to use to parse ebXML asynchronous responses.
        :param callbacks: The dictionary of callbacks to use when a message is received.
        :return:
        """
        self.ack_builder = ack_builder
        self.message_parser = message_parser
        self.callbacks = callbacks

    def post(self):
        logging.debug("POST received: %s", self.request)
        logging.debug("Body: %s", self.request.body)

        parsed_message = self.message_parser.parse_message(self.request.headers, self.request.body.decode())

        ref_to_id = parsed_message[parser.REF_TO_MESSAGE_ID]
        logging.debug("Message received is in reference to '%s'", ref_to_id)

        if ref_to_id in self.callbacks:
            self._send_ack(parsed_message)

            received_message = parsed_message[parser.MESSAGE]
            self.callbacks[ref_to_id](received_message)
        else:
            raise HTTPError(log_message=f"Could not find callback for {ref_to_id}")

    def _send_ack(self, parsed_message):
        ack_context = {
            builder.FROM_PARTY_ID: PARTY_ID,
            builder.TO_PARTY_ID: parsed_message[parser.FROM_PARTY_ID],
            builder.CPA_ID: parsed_message[parser.CPA_ID],
            builder.CONVERSATION_ID: parsed_message[parser.CONVERSATION_ID],
            ack_builder.RECEIVED_MESSAGE_TIMESTAMP: parsed_message[parser.TIMESTAMP],
            ack_builder.RECEIVED_MESSAGE_ID: parsed_message[parser.MESSAGE_ID]
        }

        _, ack_message = self.ack_builder.build_message(ack_context)

        self.set_header("Content-Type", "text/xml")
        self.write(ack_message)
