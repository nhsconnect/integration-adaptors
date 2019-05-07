import logging

from tornado.web import RequestHandler

import mhs.builder.ebxml_ack_message_builder as ack_builder
import mhs.builder.ebxml_message_builder as builder
import mhs.parser.ebxml_message_parser as parser
from mhs.sender.sender import PARTY_ID


class AsyncResponseHandler(RequestHandler):
    """A RequestHandler for asynchronous responses from a remote MHS."""

    def initialize(self, ack_builder, message_parser):
        """Initialise this request handler with the provided dependencies.

        :param ack_builder: The message builder to use when building ebXML acknowledgement messages.
        :param message_parser: The message parser to use to parse ebXML asynchronous responses.
        :return:
        """
        self.ack_builder = ack_builder
        self.message_parser = message_parser

    def post(self):
        # TODO: Configure headers correctly?

        logging.debug("POST received: %s", self.request)
        logging.debug("Body: %s", self.request.body)

        parsed_message = self.message_parser.parse_message(self.request.body)

        ack_message = self._build_ack(parsed_message)

        self.write(ack_message)

    def _build_ack(self, parsed_message):
        ack_context = {
            builder.FROM_PARTY_ID: PARTY_ID,
            builder.TO_PARTY_ID: parsed_message[parser.FROM_PARTY_ID],
            builder.CPA_ID: parsed_message[parser.CPA_ID],
            builder.CONVERSATION_ID: parsed_message[parser.CONVERSATION_ID],
            ack_builder.RECEIVED_MESSAGE_TIMESTAMP: parsed_message[parser.TIMESTAMP],
            ack_builder.RECEIVED_MESSAGE_ID: parsed_message[parser.MESSAGE_ID]
        }

        ack_message = self.ack_builder.build_message(ack_context)
        return ack_message
