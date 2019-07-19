"""This module defines the envelope used to wrap asynchronous messages to be sent to a remote MHS."""
import copy
import logging
import pathlib
import typing

import utilities.message_utilities as message_utilities
import builder.pystache_message_builder as pystache_message_builder

import mhs.common.messages.envelope as envelope
from definitions import ROOT_DIR

TEMPLATES_DIR = "data/templates"

FROM_PARTY_ID = "from_party_id"
TO_PARTY_ID = "to_party_id"
CPA_ID = "cpa_id"
CONVERSATION_ID = 'conversation_id'
MESSAGE_ID = 'message_id'
TIMESTAMP = 'timestamp'


class EbxmlEnvelope(envelope.Envelope):
    """An envelope that contains a message to be sent asynchronously to a remote MHS."""

    def __init__(self, template_file, message_dictionary: typing.Dict[str, str]):
        """Create a new EbxmlEnvelope that populates the specified template file with the provided dictionary.

        :param template_file: The template file to populate with values.
        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        self.message_dictionary = message_dictionary

        ebxml_template_dir = str(pathlib.Path(ROOT_DIR) / TEMPLATES_DIR)
        self.message_builder = pystache_message_builder.PystacheMessageBuilder(ebxml_template_dir, template_file)

    def serialize(self) -> typing.Tuple[str, str]:
        """Produce a serialised representation of this ebXML message by populating a Mustache template with this
        object's properties.

        :return: A tuple string containing the ID generated for message created and the message value.
        """
        ebxml_message_dictionary = copy.deepcopy(self.message_dictionary)

        message_id = message_utilities.MessageUtilities.get_uuid()
        ebxml_message_dictionary[MESSAGE_ID] = message_id
        timestamp = message_utilities.MessageUtilities.get_timestamp()
        ebxml_message_dictionary[TIMESTAMP] = timestamp
        logging.debug("Creating ebXML message with message ID '%s' and timestamp '%s'", message_id, timestamp)

        return message_id, self.message_builder.build_message(ebxml_message_dictionary)
