"""This module defines the envelope used to wrap asynchronous request messages to be sent to a remote MHS."""

from __future__ import annotations

import base64
import copy
import email
import email.message
import email.policy
from typing import Dict, Tuple, Union, List, Sequence, Generator
from xml.etree.ElementTree import Element

from builder import pystache_message_builder
from defusedxml import ElementTree

from comms.http_headers import HttpHeaders
from utilities import integration_adaptors_logger as log, message_utilities

from mhs_common.messages import ebxml_envelope

logger = log.IntegrationAdaptorsLogger(__name__)

EBXML_TEMPLATE = "ebxml_request"

MESSAGE = "hl7_message"

EBXML = "ebxml"

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

    def __init__(self, message_dictionary: Dict[str, Union[str, bool, List[Dict[str, Union[str, bool]]]]]):
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

    def serialize(self, _message_dictionary=None) -> Tuple[str, Dict[str, str], str]:
        message_dictionary = copy.deepcopy(self.message_dictionary)

        self._set_headers_for_attachments(message_dictionary)

        message_id, http_headers, message = super().serialize(_message_dictionary=message_dictionary)

        http_headers[HttpHeaders.CONTENT_TYPE] = EBXML_CONTENT_TYPE_VALUE
        return message_id, http_headers, message

    @staticmethod
    def _set_headers_for_attachments(message_dictionary):
        """
        Generate a content ID for each attachment and set the content transfer encoding based on whether the
        attachment is Base64-encoded or not.
        :param message_dictionary: message dictionary that has the attachments
        """
        attachment: dict
        for attachment in message_dictionary.setdefault(ATTACHMENTS, []):
            attachment[ATTACHMENT_CONTENT_ID] = f'{message_utilities.get_uuid()}@spine.nhs.uk'
            try:
                attachment[ATTACHMENT_CONTENT_TRANSFER_ENCODING] = 'base64' if attachment.pop(ATTACHMENT_BASE64) \
                    else '8bit'
            except KeyError as e:
                logger.error('Failed to find {Key} when generating message from {TemplateFile} . {ErrorMessage}',
                             fparams={
                                 'Key': f'{ATTACHMENTS}[].{ATTACHMENT_BASE64}',
                                 'TemplateFile': EBXML_TEMPLATE,
                                 'ErrorMessage': e
                             })
                raise pystache_message_builder.MessageGenerationError(f'Failed to find '
                                                                      f'key:{ATTACHMENTS}[].{ATTACHMENT_BASE64} when '
                                                                      f'generating message from template '
                                                                      f'file:{EBXML_TEMPLATE}') from e

    @classmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> EbxmlRequestEnvelope:
        """Parse the provided message string and create an instance of an EbxmlRequestEnvelope.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: An instance of an EbxmlAckEnvelope constructed from the message.
        """
        msg = EbxmlRequestEnvelope._parse_mime_message(headers, message)
        ebxml_part, payload_part, attachments = EbxmlRequestEnvelope._extract_message_parts(msg)
        xml_tree: Element = ElementTree.fromstring(ebxml_part)
        extracted_values = super().parse_message(xml_tree)

        cls._extract_more_values_from_xml_tree(xml_tree, extracted_values)

        extracted_values[EBXML] = ebxml_part
        extracted_values[ATTACHMENTS] = attachments

        if payload_part:
            extracted_values[MESSAGE] = payload_part

        return EbxmlRequestEnvelope(extracted_values)

    @classmethod
    def _extract_more_values_from_xml_tree(cls, xml_tree: Element,
                                           extracted_values: Dict[str, Union[str, bool]]):
        """
        Extract more values from XML tree (DuplicateElimination, SyncReply, AckRequested and SOAP actor). Some of the
        values extracted are booleans (ie if the element is present or not).
        :param xml_tree: XML tree to extract values from.
        :param extracted_values: Values extracted so far. The additional extracted values will be added to this dict.
        """
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
        content_type_header = f'{HttpHeaders.CONTENT_TYPE}: {headers[HttpHeaders.CONTENT_TYPE]}\r\n\r\n'

        msg = email.message_from_string(content_type_header + message, policy=email.policy.HTTP)

        if msg.defects:
            logger.warning('Found defects in MIME message during parsing. {Defects}',
                           fparams={'Defects': msg.defects})

        return msg

    @staticmethod
    def _extract_message_parts(msg: email.message.EmailMessage) -> Tuple[str, str, List[Dict[str, Union[str, bool]]]]:
        """Extract the ebXML and payload parts of the message and return them as a tuple.

        :param msg: The message to extract parts from.
        :return: A tuple containing the ebXML and payload (if present, otherwise None) parts of the message provided.
        """
        # EIS section 2.5.4 defines that the first MIME part must contain the ebML SOAP message and the message payload
        # (if present) must be the first additional attachment.

        if not msg.is_multipart():
            logger.error('Non-multipart message received')
            raise ebxml_envelope.EbXmlParsingError("Non-multipart message received")

        message_parts: Sequence[email.message.EmailMessage] = tuple(msg.iter_parts())

        EbxmlRequestEnvelope._report_any_defects_in_message_parts(message_parts)

        # ebXML part is the first part of the message
        ebxml_part = EbxmlRequestEnvelope._extract_ebxml_part(message_parts[0])

        payload_part = None
        attachments = []
        if len(message_parts) > 1:
            # HL7 payload part is the second part of the message
            payload_part = EbxmlRequestEnvelope._extract_hl7_payload_part(message_parts[1])

            # Any additional attachments are from the third part of the message onwards
            attachments.extend(EbxmlRequestEnvelope._extract_additional_attachments_parts(message_parts[2:]))

        return ebxml_part, payload_part, attachments

    @staticmethod
    def _report_any_defects_in_message_parts(message_parts: Sequence[email.message.EmailMessage]):
        for i, part in enumerate(message_parts):
            if part.defects:
                logger.warning('Found defects in {PartIndex} of MIME message during parsing. {Defects}',
                               fparams={'PartIndex': i, 'Defects': part.defects})

    @staticmethod
    def _extract_ebxml_part(message_part: email.message.EmailMessage) -> str:
        ebxml_part, is_base64_ebxml_part = EbxmlRequestEnvelope._convert_message_part_to_str(message_part)
        if is_base64_ebxml_part:
            logger.error('Failed to decode ebXML header part of message as text')
            raise ebxml_envelope.EbXmlParsingError("Failed to decode ebXML header part of message as text")
        return ebxml_part

    @staticmethod
    def _extract_hl7_payload_part(message_part: email.message.EmailMessage) -> str:
        payload_part, is_base64_payload = EbxmlRequestEnvelope._convert_message_part_to_str(message_part)
        if is_base64_payload:
            logger.error('Failed to decode HL7 payload part of message as text')
            raise ebxml_envelope.EbXmlParsingError("Failed to decode HL7 payload part of message as text")
        return payload_part

    @staticmethod
    def _extract_additional_attachments_parts(message_parts: Sequence[email.message.EmailMessage]) \
            -> Generator[Dict[Union[str, bool]]]:
        for attachment_message in message_parts:
            payload, is_base64 = EbxmlRequestEnvelope._convert_message_part_to_str(attachment_message)
            attachment = {
                ATTACHMENT_PAYLOAD: payload,
                ATTACHMENT_BASE64: is_base64,
                # The [1:-1] is to remove angle brackets (<>) that surround the content ID
                ATTACHMENT_CONTENT_ID: str(attachment_message['Content-Id'][1:-1]),
                ATTACHMENT_CONTENT_TYPE: attachment_message.get_content_type()
            }
            yield attachment

    @staticmethod
    def _convert_message_part_to_str(message_part: email.message.EmailMessage) -> Tuple[str, bool]:
        content: Union[str, bytes] = message_part.get_content()
        content_type = message_part.get_content_type()
        content_transfer_encoding = message_part['Content-Transfer-Encoding']
        logger_dict = {'ContentType': content_type, 'ContentTransferEncoding': content_transfer_encoding}

        if isinstance(content, str):
            logger.info('Successfully decoded message part with {ContentType} {ContentTransferEncoding} as string',
                        fparams=logger_dict)
            return content, False
        try:
            if content_type == 'application/xml':
                decoded_content = content.decode()
                logger.info('Successfully decoded message part with {ContentType} {ContentTransferEncoding} '
                            'as a string', fparams=logger_dict)
                return decoded_content, False
            decoded_content = base64.b64encode(content).decode()
            logger.info('Successfully encoded binary message part with {ContentType} {ContentTransferEncoding} as '
                        'a base64 string', fparams=logger_dict)
            return decoded_content, True
        except UnicodeDecodeError as e:
            logger.error('Failed to decode ebXML message part with {ContentType} {ContentTransferEncoding}.',
                         fparams=logger_dict)
            raise ebxml_envelope.EbXmlParsingError(f'Failed to decode ebXML message part with '
                                                   f'Content-Type: {content_type} and '
                                                   f'Content-Transfer-Encoding: {content_transfer_encoding}') from e
