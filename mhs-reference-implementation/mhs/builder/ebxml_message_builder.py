import copy
from pathlib import Path

from builder.pystache_message_builder import PystacheMessageBuilder
from definitions import ROOT_DIR
from utilities.message_utilities import MessageUtilities

TEMPLATES_DIR = "data/templates"

CONVERSATION_ID = 'conversation_id'
MESSAGE_ID = 'message_id'
TIMESTAMP = 'timestamp'


class EbXmlMessageBuilder(PystacheMessageBuilder):
    """A component that uses Pystache to populate a Mustache template in order to build an EBXML message."""

    def __init__(self, template_file):
        """Create a new EbXmlRequestMessageBuilder that uses an EBXML request template file.

        :param template_file: The template file to populate with values.
        """
        ebxml_template_dir = str(Path(ROOT_DIR) / TEMPLATES_DIR)

        super().__init__(ebxml_template_dir, template_file)

    def build_message(self, message_dictionary):
        """Build an ebXML message by populating a Mustache template with values from the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        :return: A string containing a message suitable for sending to a remote MHS.
        """
        ebxml_message_dictionary = copy.deepcopy(message_dictionary)

        ebxml_message_dictionary[CONVERSATION_ID] = MessageUtilities.get_uuid()
        ebxml_message_dictionary[MESSAGE_ID] = MessageUtilities.get_uuid()
        ebxml_message_dictionary[TIMESTAMP] = MessageUtilities.get_timestamp()

        return super().build_message(ebxml_message_dictionary)
