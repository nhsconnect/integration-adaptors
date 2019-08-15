"""This module defines the envelope used to wrap asynchronous messages to be sent to a remote MHS."""
import copy
import pathlib
from typing import Dict, Tuple, Any, Optional, NamedTuple
from xml.etree.ElementTree import Element

import builder.pystache_message_builder as pystache_message_builder
from definitions import ROOT_DIR
from mhs_common.messages import envelope
import utilities.message_utilities as message_utilities
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('COMMON_EBXML_ENVELOPE')

TEMPLATES_DIR = "data/templates"

FROM_PARTY_ID = "from_party_id"
TO_PARTY_ID = "to_party_id"
CPA_ID = "cpa_id"
CONVERSATION_ID = 'conversation_id'
SERVICE = "service"
ACTION = "action"
MESSAGE_ID = 'message_id'
TIMESTAMP = 'timestamp'
RECEIVED_MESSAGE_ID = "received_message_id"

EBXML_NAMESPACE = "eb"
SOAP_NAMESPACE = "SOAP"
NAMESPACES = {SOAP_NAMESPACE: "http://schemas.xmlsoap.org/soap/envelope/",
              EBXML_NAMESPACE: "http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd"}


class EbxmlEnvelope(envelope.Envelope):
    """An envelope that contains a message to be sent asynchronously to a remote MHS."""

    class _ElementToExtractWhenParsing(NamedTuple):
        name: str
        xml_name: str
        xml_parent: str = None

    _elements_to_extract_when_parsing = [
        _ElementToExtractWhenParsing(FROM_PARTY_ID, 'PartyId', xml_parent='From'),
        _ElementToExtractWhenParsing(TO_PARTY_ID, 'PartyId', xml_parent='To'),
        _ElementToExtractWhenParsing(CPA_ID, 'CPAId'),
        _ElementToExtractWhenParsing(CONVERSATION_ID, 'ConversationId'),
        _ElementToExtractWhenParsing(SERVICE, 'Service'),
        _ElementToExtractWhenParsing(ACTION, 'Action'),
        _ElementToExtractWhenParsing(MESSAGE_ID, 'MessageId', xml_parent='MessageData'),
        _ElementToExtractWhenParsing(TIMESTAMP, 'Timestamp', xml_parent='MessageData'),
        _ElementToExtractWhenParsing(RECEIVED_MESSAGE_ID, 'RefToMessageId', xml_parent='MessageData')
    ]

    def __init__(self, template_file: str, message_dictionary: Dict[str, Any]):
        """Create a new EbxmlEnvelope that populates the specified template file with the provided dictionary.

        :param template_file: The template file to populate with values.
        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        self.message_dictionary = message_dictionary

        ebxml_template_dir = str(pathlib.Path(ROOT_DIR) / TEMPLATES_DIR)
        self.message_builder = pystache_message_builder.PystacheMessageBuilder(ebxml_template_dir, template_file)

    def serialize(self) -> Tuple[str, Dict[str, str], str]:
        """Produce a serialised representation of this ebXML message by populating a Mustache template with this
        object's properties.

        :return: A tuple string containing the message ID, HTTP headers to be sent with the message and the message
        itself.
        """
        ebxml_message_dictionary = copy.deepcopy(self.message_dictionary)

        message_id = ebxml_message_dictionary.get(MESSAGE_ID)
        if not message_id:
            message_id = message_utilities.MessageUtilities.get_uuid()
            ebxml_message_dictionary[MESSAGE_ID] = message_id
        timestamp = message_utilities.MessageUtilities.get_timestamp()
        ebxml_message_dictionary[TIMESTAMP] = timestamp
        logger.info('0001', 'Creating ebXML message with {MessageId} and {Timestamp}',
                    {'MessageId': message_id, 'Timestamp': timestamp})

        message = self.message_builder.build_message(ebxml_message_dictionary)
        http_headers = {
            'charset': 'UTF-8',
            'SOAPAction': f'{ebxml_message_dictionary[SERVICE]}/{ebxml_message_dictionary[ACTION]}'
        }
        return message_id, http_headers, message

    @staticmethod
    def parse_message(xml_tree: Element) -> Dict[str, str]:
        """Extract a dictionary of values from the provided xml Element tree.

        :param xml_tree: The xml tree to extract values from
        :return: A dictionary of values extracted from the message.
        """
        extracted_values = {}

        for element_to_extract in EbxmlEnvelope._elements_to_extract_when_parsing:
            EbxmlEnvelope._add_if_present(extracted_values, element_to_extract.name,
                                          EbxmlEnvelope._extract_ebxml_text_value(xml_tree,
                                                                                  element_to_extract.xml_name,
                                                                                  parent=element_to_extract.xml_parent,
                                                                                  required=True))

        return extracted_values

    @staticmethod
    def _path_to_ebxml_element(name: str, parent: str = None) -> str:
        path = ".//"

        if parent is not None:
            path += f"{EBXML_NAMESPACE}:{parent}/"

        path += f"{EBXML_NAMESPACE}:{name}"

        return path

    @staticmethod
    def _extract_ebxml_value(xml_tree: Element, element_name: str, parent: str = None,
                             required: bool = False) -> Optional[Element]:
        xpath = EbxmlEnvelope._path_to_ebxml_element(element_name, parent=parent)
        value = xml_tree.find(xpath, namespaces=NAMESPACES)
        if value is None and required:
            logger.error('0002', "Weren't able to find required element {xpath} during parsing of EbXML message.",
                         {'xpath': xpath})
            raise EbXmlParsingError(f"Weren't able to find required element {xpath} during parsing of EbXML message")
        return value

    @staticmethod
    def _extract_ebxml_text_value(xml_tree: Element, element_name: str, parent: str = None,
                                  required: bool = False) -> Optional[str]:
        value = EbxmlEnvelope._extract_ebxml_value(xml_tree, element_name, parent, required)
        text = None

        if value is not None:
            text = value.text

        return text

    @staticmethod
    def _extract_attribute(xml_tree: Element, element_name: str, attribute_namespace: Dict[str, str],
                           attribute_name: str, values_dict: Dict[str, Any], key: str):
        xpath = EbxmlEnvelope._path_to_ebxml_element(element_name)
        element = xml_tree.find(xpath, NAMESPACES)
        if element is not None:
            try:
                values_dict[key] = element.attrib["{" + NAMESPACES[attribute_namespace] + "}" + attribute_name]
            except KeyError as e:
                logger.error('0003', "Weren't able to find required {attribute_name} of {xpath} during parsing of "
                                     "EbXML message.", {'attribute_name': attribute_name, 'xpath': xpath})
                raise EbXmlParsingError(f"Weren't able to find required attribute {attribute_name} during parsing of "
                                        f"EbXML message") from e

    @staticmethod
    def _add_if_present(values_dict: Dict[str, Any], key: str, value: Any):
        if value is not None:
            values_dict[key] = value

    @staticmethod
    def _add_flag(values_dict: Dict[str, Any], key: str, value: Optional[Any]):
        if value is not None:
            values_dict[key] = True
        else:
            values_dict[key] = False


class EbXmlParsingError(Exception):
    """Raised when an error was encountered during parsing of an ebXML message."""
    pass
