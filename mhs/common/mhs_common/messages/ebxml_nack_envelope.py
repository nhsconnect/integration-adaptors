"""This module defines the envelope used to wrap the negative acknowledgement messages to be sent to a remote MHS in
response to an asynchronous request."""

from __future__ import annotations

import copy
from typing import Dict

from defusedxml import ElementTree

import mhs_common.messages.ebxml_envelope as ebxml_envelope
import mhs_common.messages.common_ack_envelope as common_ack_envelope

EBXML_TEMPLATE = "ebxml_nack"


class EbxmlNackEnvelope(common_ack_envelope.CommonEbxmlAckEnvelope):
    """An envelope that contains a negative acknowledgement of an asynchronous request from a remote MHS."""

    def __init__(self, message_dictionary: Dict[str, str]):
        """Create a new EbxmlNackEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        message_dictionary = copy.deepcopy(message_dictionary)
        message_dictionary[ebxml_envelope.ACTION] = 'MessageError'
        super().__init__(EBXML_TEMPLATE, message_dictionary)

    @classmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> EbxmlNackEnvelope:
        """Parse the provided message string and create an instance of an EbxmlNackEnvelope.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: An instance of an EbxmlNackEnvelope constructed from the message.
        """
        message_dictionary = super().parse_message(ElementTree.fromstring(message))
        message_dictionary[common_ack_envelope.RECEIVED_MESSAGE_TIMESTAMP] = \
            message_dictionary.pop(ebxml_envelope.TIMESTAMP)
        return EbxmlNackEnvelope(message_dictionary)
