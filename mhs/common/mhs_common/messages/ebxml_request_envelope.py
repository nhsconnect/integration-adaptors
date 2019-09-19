"""This module defines the envelope used to wrap asynchronous request messages to be sent to a remote MHS."""

from __future__ import annotations

import copy
import email
import email.message
import email.policy
from typing import Dict, Tuple, Union, List, Sequence
from xml.etree.ElementTree import Element

from builder import pystache_message_builder
from defusedxml import ElementTree
from utilities import integration_adaptors_logger as log, message_utilities

from mhs_common.messages import ebxml_envelope

logger = log.IntegrationAdaptorsLogger('COMMON_EBXML_REQUEST_ENVELOPE')

EBXML_TEMPLATE = "ebxml_request"

MESSAGE = "hl7_message"

CONTENT_TYPE_HEADER_NAME = "Content-Type"

DUPLICATE_ELIMINATION = "duplicate_elimination"
ACK_REQUESTED = "ack_requested"
ACK_SOAP_ACTOR = "ack_soap_actor"
SYNC_REPLY = "sync_reply"

ATTACHMENTS = 'attachments'
ATTACHMENT_CONTENT_ID = 'content_id'
ATTACHMENT_CONTENT_TYPE = 'content_type'
ATTACHMENT_BASE64 = 'is_base64'
ATTACHMENT_CONTENT_TRANSFER_ENCODING = 'content_transfer_encoding'
ATTACHMENT_PAYLOAD = 'payload'
ATTACHMENT_DESCRIPTION = 'description'
EBXML_CONTENT_TYPE_VALUE = 'multipart/related; boundary="--=_MIME-Boundary"; type=text/xml; ' \
                           'start=ebXMLHeader@spine.nhs.uk'


class EbxmlRequestEnvelope(ebxml_envelope.EbxmlEnvelope):
    """An envelope that contains a request to be sent asynchronously to a remote MHS."""

    def __init__(self, message_dictionary: Dict[str, Union[str, bool, List[Dict[str, str]]]]):
        """Create a new EbxmlRequestEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.

        Example `message_dictionary`::

            {
                'from_party_id': 'TESTGEN-201324',
                'to_party_id': 'YEA-0000806',
                'cpa_id': 'S1001A1630',
                'conversation_id': '79F49A34-9798-404C-AEC4-FD38DD81C138',
                'service': 'urn:nhs:names:services:pdsquery',
                'action': 'QUPA_IN000006UK02',
                'duplicate_elimination': True,
                'ack_requested': True,
                'ack_soap_actor': 'urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH',
                'sync_reply': True,
                'hl7_message': '<QUPA_IN000006UK02 xmlns="urn:hl7-org:v3"></QUPA_IN000006UK02>',
                'attachments': [ # Optional, defaults to empty list if not set
                    {
                        'content_type': 'text/plain',
                        'payload': 'Some text here',
                        'is_base64': False,
                        'description': 'Attachment description'
                    },
                    {
                        'content_type': 'image/png',
                        'payload': 'base64-encoded content here',
                        'is_base64': True,
                        'description': 'Another attachment description'
                    }
                ]
            }
        """
        super().__init__(EBXML_TEMPLATE, message_dictionary)

    def serialize(self, message_dictionary=None) -> Tuple[str, Dict[str, str], str]:
        message_dictionary = copy.deepcopy(self.message_dictionary)

        attachment: dict
        for attachment in message_dictionary.setdefault(ATTACHMENTS, []):
            attachment[ATTACHMENT_CONTENT_ID] = message_utilities.MessageUtilities.get_uuid()
            try:
                attachment[ATTACHMENT_CONTENT_TRANSFER_ENCODING] = 'base64' if attachment.pop(ATTACHMENT_BASE64) \
                    else '8bit'
            except KeyError as e:
                logger.error('0001',
                             'Failed to find {Key} when generating message from {TemplateFile} . {ErrorMessage}',
                             {'Key': f'{ATTACHMENTS}[].{ATTACHMENT_BASE64}', 'TemplateFile': EBXML_TEMPLATE,
                              'ErrorMessage': e})
                raise pystache_message_builder.MessageGenerationError(f'Failed to find '
                                                                      f'key:{ATTACHMENTS}[].{ATTACHMENT_BASE64} when '
                                                                      f'generating message from template '
                                                                      f'file:{EBXML_TEMPLATE}') from e

        message_id, http_headers, message = super().serialize(message_dictionary=message_dictionary)

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

        logger.info('0002', 'Extracted {extracted_values} from message', {'extracted_values': extracted_values})

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
    def _parse_mime_message(headers: Dict[str, str], message: str) -> email.message.EmailMessage:
        """ Take the provided message string (and set of HTTP headers received with it) and parse it to obtain a Message
        object.

        :param headers: The HTTP headers received with the message.
        :param message: The message (as a string) to be parsed.
        :return: a Message that represents the message received.
        """
        content_type_header = f'{CONTENT_TYPE_HEADER_NAME}: {headers[CONTENT_TYPE_HEADER_NAME]}\r\n\r\n'

        msg = email.message_from_string(content_type_header + message, policy=email.policy.HTTP)

        if msg.defects:
            logger.warning('0003', 'Found defects in MIME message during parsing. {Defects}',
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

        message_parts: Sequence[email.message.EmailMessage] = tuple(msg.iter_parts())

        for i, part in enumerate(message_parts):
            if part.defects:
                logger.warning('0004', 'Found defects in {PartIndex} of MIME message during parsing. {Defects}',
                               {'PartIndex': i, 'Defects': part.defects})

        ebxml_part = message_parts[0].get_content()

        payload_part = None
        if len(message_parts) > 1:
            payload_part = message_parts[1].get_content()

        return ebxml_part, payload_part
