"""This module defines the envelope used to wrap the common acknowledgement messages to be sent to a remote MHS in
response to an asynchronous request."""

from __future__ import annotations

import copy
from abc import abstractmethod
from typing import Dict, Tuple

import mhs_common.messages.ebxml_envelope as ebxml_envelope
from comms.http_headers import HttpHeaders

RECEIVED_MESSAGE_TIMESTAMP = "received_message_timestamp"


class CommonEbxmlAckEnvelope(ebxml_envelope.EbxmlEnvelope):
    """
    Common functionality for an envelope that contains a (positive or negative) acknowledgement of an
    asynchronous request from a remote MHS.
    """

    def __init__(self, template_file: str, message_dictionary: Dict[str, str]):
        """Create a new CommonEbxmlAckEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        :param template_file: The mustache template for the ack
        """
        message_dictionary = copy.deepcopy(message_dictionary)
        message_dictionary[ebxml_envelope.SERVICE] = 'urn:oasis:names:tc:ebxml-msg:service'

        super().__init__(template_file, message_dictionary)

    def serialize(self, _message_dictionary=None) -> Tuple[str, Dict[str, str], str]:
        message_id, http_headers, message = super().serialize()
        http_headers[HttpHeaders.CONTENT_TYPE] = 'text/xml'
        return message_id, http_headers, message

    @abstractmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> CommonEbxmlAckEnvelope:
        raise NotImplementedError
