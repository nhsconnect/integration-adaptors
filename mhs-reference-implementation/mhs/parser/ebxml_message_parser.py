FROM_PARTY_ID = "from_party_id"
CPA_ID = "cpa_id"
CONVERSATION_ID = "conversation_id"
MESSAGE_ID = "message_id"
TIMESTAMP = "timestamp"


class EbXmlMessageParser:
    """A component that extracts information from ebXML messages."""

    def parse_message(self, message):
        """Parse the provided ebXML message and extract a dictionary of values from it.

        :param message: The message to be parsed.
        :return: A dictionary of values extracted from the message.
        """
        # TODO: Implement schematron/XSLT parsing here.
        pass


class EbXmlRequestMessageParser(EbXmlMessageParser):
    """A component that extracts information from ebXML acknowledgement messages."""

    # TODO: Will contain the path the the ack-specific schematron/XSLT file.

    def parse_message(self, message):
        """Parse the provided ebXML request message and extract a dictionary of values from it.

        :param message: The message to be parsed.
        :return: A dictionary of values extracted from the message.
        """
        return {
            FROM_PARTY_ID: "YES-0000806",
            CPA_ID: "S1001A1630",
            CONVERSATION_ID: "10F5A436-1913-43F0-9F18-95EA0E43E61A",
            MESSAGE_ID: "C614484E-4B10-499A-9ACD-5D645CFACF61",
            TIMESTAMP: "2019-05-04T20:55:16Z"
        }
