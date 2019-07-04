
from builder.pystache_message_builder import PystacheMessageBuilder
from definitions import ROOT_DIR
from pathlib import Path

TEMPLATES_DIR = "selenium_tests/data/templates"


class MustacheMessageBuilder(PystacheMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build a json message."""

    def __init__(self, template_file):
        """Create a new JSONMessageBuilder that uses a json request template file.

        :param template_file: The template file to populate with values.
        """
        template_dir = str(Path(ROOT_DIR) / TEMPLATES_DIR)

        super().__init__(template_dir, template_file)
