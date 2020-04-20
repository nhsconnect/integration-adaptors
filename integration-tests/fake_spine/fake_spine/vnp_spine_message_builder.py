from pathlib import Path

from fake_spine import fake_spine_configuration
from fake_spine.pystache_message_builder import PystacheMessageBuilder

TEMPLATES_DIR = "vnp_responses"


class VnpMessageBuilder(PystacheMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build a message."""

    def __init__(self, template_file):
        """Create a new MessageBuilder that uses a mustache request template file.

        :param template_file: The template file to populate with values.
        """
        config = fake_spine_configuration.FakeSpineConfiguration()
        template_dir = str(Path(config.ROOT_DIR) / TEMPLATES_DIR)

        super().__init__(template_dir, template_file)
