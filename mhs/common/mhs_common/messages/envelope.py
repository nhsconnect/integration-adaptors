"""This module defines the base envelope used to wrap messages to be sent to a remote MHS."""

from __future__ import annotations

import abc
import pathlib
from typing import Dict, Tuple, Any

from builder import pystache_message_builder

from definitions import ROOT_DIR

FROM_PARTY_ID = "from_party_id"
TO_PARTY_ID = "to_party_id"
CPA_ID = "cpa_id"
CONVERSATION_ID = 'conversation_id'
SERVICE = "service"
ACTION = "action"
MESSAGE_ID = 'message_id'
TIMESTAMP = 'timestamp'
TO_ASID = 'to_asid'
FROM_ASID = 'from_asid'
RECEIVED_MESSAGE_ID = "received_message_id"
TEMPLATES_DIR = "data/templates"

class Envelope(abc.ABC):
    """An envelope that contains a message to be sent to a remote MHS."""

    def __init__(self, template_file: str, message_dictionary: Dict[str, Any]):
        """Create a new EbxmlEnvelope that populates the specified template file with the provided dictionary.

        :param template_file: The template file to populate with values.
        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        self.message_dictionary = message_dictionary

        ebxml_template_dir = str(pathlib.Path(ROOT_DIR) / TEMPLATES_DIR)
        self.message_builder = pystache_message_builder.PystacheMessageBuilder(ebxml_template_dir, template_file)

    @abc.abstractmethod
    def serialize(self) -> Tuple[str, Dict[str, str], str]:
        """Produce a serialised representation of this message.

        :return: A tuple of: the message id, headers to send along with the message and the serialized representation
        of the message.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> Envelope:
        """Parse the provided message string and create an instance of an Envelope.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: An instance of an Envelope constructed from the message.
        """
        pass
