import email
import email.policy
import logging
import xml.etree.ElementTree as ET
from email.message import Message
from typing import Dict, Tuple

FROM_PARTY_ID = "from_party_id"
TO_PARTY_ID = "to_party_id"
CPA_ID = "cpa_id"
CONVERSATION_ID = "conversation_id"
SERVICE = "service"
ACTION = "action"
MESSAGE_ID = "message_id"
TIMESTAMP = "timestamp"
REF_TO_MESSAGE_ID = "ref_to_message_id"
DUPLICATE_ELIMINATION = "duplicate_elimination"
ACK_REQUESTED = "ack_requested"
ACK_SOAP_ACTOR = "ack_soap_actor"
SYNC_REPLY = "sync_reply"

MESSAGE = "message"

EBXML_NAMESPACE = "eb"
SOAP_NAMESPACE = "SOAP"
NAMESPACES = {SOAP_NAMESPACE: "http://schemas.xmlsoap.org/soap/envelope/",
              EBXML_NAMESPACE: "http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd"}

CONTENT_TYPE_HEADER_NAME = "Content-Type"


class EbXmlParsingError(Exception):
    """Raised when an error was encountered during parsing of an ebXML message."""
    pass


class EbXmlMessageParser:
    """A component that extracts information from ebXML messages."""

    def parse_message(self, headers, message):
        """Parse the provided ebXML message and extract a dictionary of values from it.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: A dictionary of values extracted from the message.
        """
        xml_tree = ET.fromstring(message)
        extracted_values = {}

        self._add_if_present(extracted_values, FROM_PARTY_ID,
                             self._extract_ebxml_text_value(xml_tree, "PartyId", parent="From"))
        self._add_if_present(extracted_values, TO_PARTY_ID,
                             self._extract_ebxml_text_value(xml_tree, "PartyId", parent="To"))
        self._add_if_present(extracted_values, CPA_ID, self._extract_ebxml_text_value(xml_tree, "CPAId"))
        self._add_if_present(extracted_values, CONVERSATION_ID,
                             self._extract_ebxml_text_value(xml_tree, "ConversationId"))
        self._add_if_present(extracted_values, SERVICE, self._extract_ebxml_text_value(xml_tree, "Service"))
        self._add_if_present(extracted_values, ACTION, self._extract_ebxml_text_value(xml_tree, "Action"))
        self._add_if_present(extracted_values, MESSAGE_ID,
                             self._extract_ebxml_text_value(xml_tree, "MessageId", parent="MessageData"))
        self._add_if_present(extracted_values, TIMESTAMP,
                             self._extract_ebxml_text_value(xml_tree, "Timestamp", parent="MessageData"))
        self._add_if_present(extracted_values, REF_TO_MESSAGE_ID,
                             self._extract_ebxml_text_value(xml_tree, "RefToMessageId", parent="MessageData"))
        self._add_flag_if_present(extracted_values, DUPLICATE_ELIMINATION,
                                  self._extract_ebxml_value(xml_tree, "DuplicateElimination"))
        self._add_flag_if_present(extracted_values, SYNC_REPLY, self._extract_ebxml_value(xml_tree, "SyncReply"))
        self._add_flag_if_present(extracted_values, ACK_REQUESTED, self._extract_ebxml_value(xml_tree, "AckRequested"))
        self._extract_attribute(xml_tree, "AckRequested", SOAP_NAMESPACE, "actor", extracted_values, ACK_SOAP_ACTOR)

        return extracted_values

    def _path_to_ebxml_element(self, name, parent=None):
        path = ".//"

        if parent is not None:
            path += EBXML_NAMESPACE + ":" + parent + "/"

        path += EBXML_NAMESPACE + ":" + name

        return path

    def _extract_ebxml_value(self, xml_tree, element_name, parent=None):
        xpath = self._path_to_ebxml_element(element_name, parent=parent)
        return xml_tree.find(xpath, namespaces=NAMESPACES)

    def _extract_ebxml_text_value(self, xml_tree, element_name, parent=None):
        value = self._extract_ebxml_value(xml_tree, element_name, parent)
        text = None

        if value is not None:
            text = value.text

        return text

    def _extract_attribute(self, xml_tree, element_name, attribute_namespace, attribute_name, values_dict, key):
        xpath = self._path_to_ebxml_element(element_name)
        element = xml_tree.find(xpath, NAMESPACES)
        if element is not None:
            values_dict[key] = element.attrib["{" + NAMESPACES[attribute_namespace] + "}" + attribute_name]

    def _add_if_present(self, values_dict, key, value):
        if value is not None:
            values_dict[key] = value

    def _add_flag_if_present(self, values_dict, key, value):
        if value is not None:
            values_dict[key] = True


class EbXmlRequestMessageParser(EbXmlMessageParser):
    """A component that extracts information from ebXML request messages."""

    def parse_message(self, headers, message):
        """Parse the provided ebXML request message and extract a dictionary of values from it.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: A dictionary of values extracted from the message.
        """
        msg = self._parse_mime_message(headers, message)
        ebxml_part, payload_part = self._extract_message_parts(msg)
        extracted_values = super().parse_message(headers, ebxml_part)

        if payload_part:
            extracted_values[MESSAGE] = payload_part

        logging.debug("Extracted values from message: %s", extracted_values)
        return extracted_values

    def _parse_mime_message(self, headers: Dict[str, str], message: str) -> Message:
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

    def _extract_message_parts(self, msg) -> Tuple[str, str]:
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
