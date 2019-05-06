from tornado.web import RequestHandler

import mhs.builder.ebxml_ack_message_builder as ack_builder
import mhs.builder.ebxml_message_builder as builder
import mhs.parser.ebxml_message_parser as parser
from mhs.sender.sender import PARTY_ID

MESSAGE_PARSER = "message_parser"
ACK_BUILDER = "ack_builder"
CALLBACKS = "callbacks"


class AsyncResponseReceiver(RequestHandler):
    """A RequestHandler for asynchronous responses from a remote MHS."""

    def initialize(self, initialisation_dict):
        """Initialise this request handler with the provided dictionary of initialisation arguments.

        :param initialisation_dict: A dictionary of initialisation arguments.
        """
        self.ack_builder = initialisation_dict[ACK_BUILDER]
        self.message_parser = initialisation_dict[MESSAGE_PARSER]

    def post(self):
        print(f"POST received: {self.request}")

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
