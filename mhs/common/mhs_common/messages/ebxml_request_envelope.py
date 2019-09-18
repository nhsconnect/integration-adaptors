"""This module defines the envelope used to wrap asynchronous request messages to be sent to a remote MHS."""

from __future__ import annotations

import email
import email.message
import email.policy
from typing import Dict, Tuple, Union
from xml.etree.ElementTree import Element

from defusedxml import ElementTree
from utilities import integration_adaptors_logger as log

from mhs_common.messages import ebxml_envelope

logger = log.IntegrationAdaptorsLogger('COMMON_EBXML_REQUEST_ENVELOPE')

EBXML_TEMPLATE = "ebxml_request"

MESSAGE = "hl7_message"

CONTENT_TYPE_HEADER_NAME = "Content-Type"

DUPLICATE_ELIMINATION = "duplicate_elimination"
ACK_REQUESTED = "ack_requested"
ACK_SOAP_ACTOR = "ack_soap_actor"
SYNC_REPLY = "sync_reply"

EBXML_CONTENT_TYPE_VALUE = 'multipart/related; boundary="--=_MIME-Boundary"; type=text/xml; ' \
                           'start=ebXMLHeader@spine.nhs.uk'


class EbxmlRequestEnvelope(ebxml_envelope.EbxmlEnvelope):
    """An envelope that contains a request to be sent asynchronously to a remote MHS."""

    def __init__(self, message_dictionary: Dict[str, Union[str, bool]]):
        """Create a new EbxmlRequestEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        super().__init__(EBXML_TEMPLATE, message_dictionary)

    def serialize(self) -> Tuple[str, Dict[str, str], str]:
        message_id, http_headers, message = super().serialize()
        http_headers[CONTENT_TYPE_HEADER_NAME] = EBXML_CONTENT_TYPE_VALUE
        return message_id, http_headers, message

    @classmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> EbxmlRequestEnvelope:
        """Parse the provided message string and create an instance of an EbxmlRequestEnvelope.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: An instance of an EbxmlAckEnvelope constructed from the message.
        """
        msg = EbxmlRequestEnvelope._parse_mime_message(headers, message)
        ebxml_part, payload_part = EbxmlRequestEnvelope._extract_message_parts(msg)
        xml_tree = ElementTree.fromstring(ebxml_part)
        extracted_values = super().parse_message(xml_tree)

        cls._extract_more_values_from_xml_tree(xml_tree, extracted_values)

        logger.info('0001', 'Extracted {extracted_values} from message', {'extracted_values': extracted_values})

        if payload_part:
            extracted_values[MESSAGE] = payload_part

        return EbxmlRequestEnvelope(extracted_values)

    @classmethod
    def _extract_more_values_from_xml_tree(cls, xml_tree: Element,
                                           extracted_values: Dict[str, Union[str, bool]]):
        cls._add_flag(extracted_values, DUPLICATE_ELIMINATION,
                      cls._extract_ebxml_value(xml_tree, "DuplicateElimination"))
        cls._add_flag(extracted_values, SYNC_REPLY, cls._extract_ebxml_value(xml_tree, "SyncReply"))
        cls._add_flag(extracted_values, ACK_REQUESTED, cls._extract_ebxml_value(xml_tree, "AckRequested"))
        cls._extract_attribute(xml_tree, "AckRequested", ebxml_envelope.SOAP_NAMESPACE, "actor", extracted_values,
                               ACK_SOAP_ACTOR)

    @staticmethod
    def _parse_mime_message(headers: Dict[str, str], message: str) -> email.message.Message:
        """ Take the provided message string (and set of HTTP headers received with it) and parse it to obtain a Message
        object.

        :param headers: The HTTP headers received with the message.
        :param message: The message (as a string) to be parsed.
        :return: a Message that represents the message received.
        """
        content_type_header = f'{CONTENT_TYPE_HEADER_NAME}: {headers[CONTENT_TYPE_HEADER_NAME]}\r\n\r\n'

        msg = email.message_from_string(content_type_header + message, policy=email.policy.HTTP)

        if msg.defects:
            logger.warning('0002', 'Found defects in MIME message during parsing. {Defects}',
                           {'Defects': msg.defects})

        return msg

    @staticmethod
    def _extract_message_parts(msg: email.message.EmailMessage) -> Tuple[str, str]:
        """Extract the ebXML and payload parts of the message and return them as a tuple.

        :param msg: The message to extract parts from.
        :return: A tuple containing the ebXML and payload (if present, otherwise None) parts of the message provided.
        """
        # EIS section 2.5.4 defines that the first MIME part must contain the ebML SOAP message and the message payload
        # (if present) must be the first additional attachment.

        if not msg.is_multipart():
            raise ebxml_envelope.EbXmlParsingError("Non-multipart message received!")

        message_parts = tuple(msg.iter_parts())

        for i, part in enumerate(message_parts):
            if part.defects:
                logger.warning('0003', 'Found defects in {PartIndex} of MIME message during parsing. {Defects}',
                               {'PartIndex': i, 'Defects': part.defects})

        ebxml_part = message_parts[0].get_payload()

        payload_part = None
        if len(message_parts) > 1:
            payload_part = message_parts[1].get_payload()

        return ebxml_part, payload_part
