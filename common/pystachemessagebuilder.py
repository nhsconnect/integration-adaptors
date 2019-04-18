"""A module that defines a Pystache-based MessageBuilder."""
import pystache
from pystache import Renderer


class PystacheMessageBuilder:
    """A component that uses Pystache to populate a Mustache template in order to build a message."""

    def __init__(self, template_dir, template_file):
        """Create a new PystacheMessageBuilder that uses the specified template file.
        :param template_dir: The directory to load template files from
        :param template_file: The template file to populate with values.
        """
        self._renderer = Renderer(search_dirs=template_dir)
        raw_template = self._renderer.load_template(template_file)
        self._parsed_template = pystache.parse(raw_template)

    def build_message(self, message_dictionary):
        """Build a message by populating a Mustache template with values from the provided dictionary.
        :param message_dictionary: The dictionary of values to use when populating the template.
        :return: A string containing a message suitable for sending to a remote MHS.
        """
        return self._renderer.render(self._parsed_template, message_dictionary)