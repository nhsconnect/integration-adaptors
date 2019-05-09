from mhs.builder.ebxml_message_builder import EbXmlMessageBuilder

EBXML_TEMPLATE = "ebxml_request"

SERVICE = "service"
ACTION = "action"
DUPLICATE_ELIMINATION = "duplicate_elimination"
ACK_REQUESTED = "ack_requested"
ACK_SOAP_ACTOR = "ack_soap_actor"
SYNC_REPLY = "sync_reply"
MESSAGE = "hl7_message"


class EbXmlRequestMessageBuilder(EbXmlMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build an EBXML request message."""

    def __init__(self):
        """Create a new EbXmlRequestMessageBuilder that uses an EBXML request template file."""
        super().__init__(EBXML_TEMPLATE)
