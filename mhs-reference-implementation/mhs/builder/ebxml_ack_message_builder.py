from mhs.builder.ebxml_message_builder import EbXmlMessageBuilder

EBXML_TEMPLATE = "ebxml_ack"


class EbXmlAckMessageBuilder(EbXmlMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build an EBXML acknowledgment
    message."""

    def __init__(self):
        """Create a new EbXmlAckMessageBuilder that uses an EBXML request template file."""
        super().__init__(EBXML_TEMPLATE)
