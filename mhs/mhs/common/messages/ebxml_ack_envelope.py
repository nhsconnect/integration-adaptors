"""This module defines the envelope used to wrap the acknowledgement messages to be sent to a remote MHS in response to
an asynchronous request."""

from __future__ import annotations

from typing import Dict
from xml.etree import ElementTree

import mhs.common.messages.ebxml_envelope as ebxml_envelope

EBXML_TEMPLATE = "ebxml_ack"

RECEIVED_MESSAGE_TIMESTAMP = "received_message_timestamp"


class EbxmlAckEnvelope(ebxml_envelope.EbxmlEnvelope):
    """An envelope that contains an acknowledgement of an asynchronous request from a remote MHS."""

    def __init__(self, message_dictionary: Dict[str, str]):
        """Create a new EbxmlAckEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        super().__init__(EBXML_TEMPLATE, message_dictionary)

    @classmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> EbxmlAckEnvelope:
        """Parse the provided message string and create an instance of an EbxmlAckEnvelope.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: An instance of an EbxmlAckEnvelope constructed from the message.
        """
        message_dictionary = super().parse_message(ElementTree.fromstring(message))
        message_dictionary[RECEIVED_MESSAGE_TIMESTAMP] = message_dictionary.pop(ebxml_envelope.TIMESTAMP)
        return EbxmlAckEnvelope(message_dictionary)
