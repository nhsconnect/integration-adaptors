"""This module defines the envelope used to wrap asynchronous request messages to be sent to a remote MHS."""

from __future__ import annotations

import email
import email.message
import email.policy
import logging
from typing import Dict, Tuple
from xml.etree import ElementTree

import mhs.common.messages.ebxml_envelope as ebxml_envelope

EBXML_TEMPLATE = "ebxml_request"

MESSAGE = "hl7_message"

CONTENT_TYPE_HEADER_NAME = "Content-Type"


class EbXmlParsingError(Exception):
    """Raised when an error was encountered during parsing of an ebXML message."""
    pass


class EbxmlRequestEnvelope(ebxml_envelope.EbxmlEnvelope):
    """An envelope that contains a request to be sent asynchronously to a remote MHS."""

    def __init__(self, message_dictionary: Dict[str, str]):
        """Create a new EbxmlRequestEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        super().__init__(EBXML_TEMPLATE, message_dictionary)

    @classmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> EbxmlRequestEnvelope:
        """Parse the provided message string and create an instance of an EbxmlRequestEnvelope.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: An instance of an EbxmlAckEnvelope constructed from the message.
        """
        msg = EbxmlRequestEnvelope._parse_mime_message(headers, message)
        ebxml_part, payload_part = EbxmlRequestEnvelope._extract_message_parts(msg)
        extracted_values = super().parse_message(ElementTree.fromstring(ebxml_part))

        if payload_part:
            extracted_values[MESSAGE] = payload_part

        logging.debug("Extracted values from message: %s", extracted_values)
        return EbxmlRequestEnvelope(extracted_values)

    @staticmethod
    def _parse_mime_message(headers: Dict[str, str], message: str) -> email.message.Message:
        """ Take the provided message string (and set of HTTP headers received with it) and parse it to obtain a Message
        object.

        :param headers: The HTTP headers received with the message.
        :param message: The message (as a string) to be parsed.
        :return: a Message that represents the message received.
        """
        content_type = headers[CONTENT_TYPE_HEADER_NAME]
        content_type_header = CONTENT_TYPE_HEADER_NAME + ": " + content_type + "\r\n"

        msg = email.message_from_string(content_type_header + message)

        return msg

    @staticmethod
    def _extract_message_parts(msg: email.message.Message) -> Tuple[str, str]:
        """Extract the ebXML and payload parts of the message and return them as a tuple.

        :param msg: The message to extract parts from.
        :return: A tuple containing the ebXML and payload (if present, otherwise None) parts of the message provided.
        """
        # EIS section 2.5.4 defines that the first MIME part must contain the ebML SOAP message and the message payload
        # (if present) must be the first additional attachment.

        if not msg.is_multipart():
            raise EbXmlParsingError("Non-multipart message received!")

        message_parts = msg.get_payload()

        ebxml_part = message_parts[0].get_payload()

        payload_part = None
        if len(message_parts) > 1:
            payload_part = message_parts[1].get_payload()

        return ebxml_part, payload_part
