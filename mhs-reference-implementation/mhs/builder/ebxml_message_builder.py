from pathlib import Path

from builder.pystache_message_builder import PystacheMessageBuilder
from definitions import ROOT_DIR

TEMPLATES_DIR = "data/templates"


class EbXmlMessageBuilder(PystacheMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build an EBXML message."""

    def __init__(self, template_file):
        """Create a new EbXmlRequestMessageBuilder that uses an EBXML request template file.

        :param template_file: The template file to populate with values.
        """
        ebxml_template_dir = str(Path(ROOT_DIR) / TEMPLATES_DIR)

        super().__init__(ebxml_template_dir, template_file)
