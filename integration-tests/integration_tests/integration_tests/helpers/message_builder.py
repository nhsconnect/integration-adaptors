
from builder import pystache_message_builder
from pathlib import Path
from integration_tests.test_definitions import ROOT_DIR

TEMPLATES_DIR = "data/templates"


class MustacheMessageBuilder(pystache_message_builder.PystacheMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build a message."""

    def __init__(self, template_file):
        """Create a new MessageBuilder that uses a mustache request template file.

        :param template_file: The template file to populate with values.
        """
        template_dir = str(Path(ROOT_DIR) / TEMPLATES_DIR)

        super().__init__(template_dir, template_file)
