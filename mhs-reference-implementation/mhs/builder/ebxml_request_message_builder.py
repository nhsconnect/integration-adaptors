"""A module that defines an EBXML-specific extension of PystacheMessageBuilder."""
from pathlib import Path

from builder.pystache_message_builder import PystacheMessageBuilder
from definitions import ROOT_DIR

TEMPLATES_DIR = "data/templates"
EBXML_TEMPLATE = "ebxml_request"


class EbXmlRequestMessageBuilder(PystacheMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build an EBXML message."""

    def __init__(self):
        """Create a new EbXmlRequestMessageBuilder that uses an EBXML request template file."""
        ebxml_template_dir = str(Path(ROOT_DIR) / TEMPLATES_DIR)

        super().__init__(ebxml_template_dir, EBXML_TEMPLATE)
