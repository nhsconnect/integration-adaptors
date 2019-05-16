import copy
import logging
from pathlib import Path
from typing import Dict, Tuple

from builder.pystache_message_builder import PystacheMessageBuilder
from definitions import ROOT_DIR
from utilities.message_utilities import MessageUtilities

TEMPLATES_DIR = "data/templates"

FROM_PARTY_ID = "from_party_id"
TO_PARTY_ID = "to_party_id"
CPA_ID = "cpa_id"
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

    def build_message(self, message_dictionary: Dict[str, str]) -> Tuple[str, str]:
        """Build an ebXML message by populating a Mustache template with values from the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        :return: A tuple string containing the ID generated for message created and the message value.
        """
        ebxml_message_dictionary = copy.deepcopy(message_dictionary)

        message_id = MessageUtilities.get_uuid()
        ebxml_message_dictionary[MESSAGE_ID] = message_id
        timestamp = MessageUtilities.get_timestamp()
        ebxml_message_dictionary[TIMESTAMP] = timestamp
        logging.debug("Creating ebXML message with message ID '%s' and timestamp '%s'", message_id, timestamp)

        return message_id, super().build_message(ebxml_message_dictionary)
