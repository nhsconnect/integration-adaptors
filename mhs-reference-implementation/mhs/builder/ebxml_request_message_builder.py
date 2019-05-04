from mhs.builder.ebxml_message_builder import EbXmlMessageBuilder

EBXML_TEMPLATE = "ebxml_request"


class EbXmlRequestMessageBuilder(EbXmlMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build an EBXML request message."""

    def __init__(self):
        """Create a new EbXmlRequestMessageBuilder that uses an EBXML request template file."""
        super().__init__(EBXML_TEMPLATE)
