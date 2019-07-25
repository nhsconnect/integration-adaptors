"""This module defines the envelope used to wrap asynchronous messages to be sent to a remote MHS."""
import copy
import pathlib
import typing
import xml.etree.ElementTree as ElementTree

import builder.pystache_message_builder as pystache_message_builder
import definitions
import mhs.common.messages.envelope as envelope
import utilities.message_utilities as message_utilities
from utilities.integration_adaptors_logger import IntegrationAdaptorsLogger

logger = IntegrationAdaptorsLogger('MSGPACKER')

TEMPLATES_DIR = "data/templates"

FROM_PARTY_ID = "from_party_id"
TO_PARTY_ID = "to_party_id"
CPA_ID = "cpa_id"
CONVERSATION_ID = 'conversation_id'
SERVICE = "service"
ACTION = "action"
MESSAGE_ID = 'message_id'
TIMESTAMP = 'timestamp'
REF_TO_MESSAGE_ID = "ref_to_message_id"
DUPLICATE_ELIMINATION = "duplicate_elimination"
ACK_REQUESTED = "ack_requested"
ACK_SOAP_ACTOR = "ack_soap_actor"
SYNC_REPLY = "sync_reply"

EBXML_NAMESPACE = "eb"
SOAP_NAMESPACE = "SOAP"
NAMESPACES = {SOAP_NAMESPACE: "http://schemas.xmlsoap.org/soap/envelope/",
              EBXML_NAMESPACE: "http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd"}


class EbxmlEnvelope(envelope.Envelope):
    """An envelope that contains a message to be sent asynchronously to a remote MHS."""

    def __init__(self, template_file, message_dictionary: typing.Dict[str, str]):
        """Create a new EbxmlEnvelope that populates the specified template file with the provided dictionary.

        :param template_file: The template file to populate with values.
        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        self.message_dictionary = message_dictionary

        ebxml_template_dir = str(pathlib.Path(definitions.ROOT_DIR) / TEMPLATES_DIR)
        self.message_builder = pystache_message_builder.PystacheMessageBuilder(ebxml_template_dir, template_file)

    def serialize(self) -> typing.Tuple[str, str]:
        """Produce a serialised representation of this ebXML message by populating a Mustache template with this
        object's properties.

        :return: A tuple string containing the ID generated for message created and the message value.
        """
        ebxml_message_dictionary = copy.deepcopy(self.message_dictionary)

        message_id = message_utilities.MessageUtilities.get_uuid()
        ebxml_message_dictionary[MESSAGE_ID] = message_id
        timestamp = message_utilities.MessageUtilities.get_timestamp()
        ebxml_message_dictionary[TIMESTAMP] = timestamp
        logger.info('0001', 'Creating ebXML message with {MessageId} and {Timestamp}', {'MessageId': message_id, 'Timestamp': timestamp})

        return message_id, self.message_builder.build_message(ebxml_message_dictionary)

    @staticmethod
    def parse_message(headers: typing.Dict[str, str], message: str) -> typing.Dict[str, str]:
        """Parse the provided ebXML message and extract a dictionary of values from it.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: A dictionary of values extracted from the message.
        """
        xml_tree = ElementTree.fromstring(message)
        extracted_values = {}

        EbxmlEnvelope._add_if_present(extracted_values, FROM_PARTY_ID,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "PartyId", parent="From"))
        EbxmlEnvelope._add_if_present(extracted_values, TO_PARTY_ID,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "PartyId", parent="To"))
        EbxmlEnvelope._add_if_present(extracted_values, CPA_ID,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "CPAId"))
        EbxmlEnvelope._add_if_present(extracted_values, CONVERSATION_ID,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "ConversationId"))
        EbxmlEnvelope._add_if_present(extracted_values, SERVICE,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "Service"))
        EbxmlEnvelope._add_if_present(extracted_values, ACTION,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "Action"))
        EbxmlEnvelope._add_if_present(extracted_values, MESSAGE_ID,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "MessageId",
                                                                              parent="MessageData"))
        EbxmlEnvelope._add_if_present(extracted_values, TIMESTAMP,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "Timestamp",
                                                                              parent="MessageData"))
        EbxmlEnvelope._add_if_present(extracted_values, REF_TO_MESSAGE_ID,
                                      EbxmlEnvelope._extract_ebxml_text_value(xml_tree, "RefToMessageId",
                                                                              parent="MessageData"))
        EbxmlEnvelope._add_flag_if_present(extracted_values, DUPLICATE_ELIMINATION,
                                           EbxmlEnvelope._extract_ebxml_value(xml_tree, "DuplicateElimination"))
        EbxmlEnvelope._add_flag_if_present(extracted_values, SYNC_REPLY,
                                           EbxmlEnvelope._extract_ebxml_value(xml_tree, "SyncReply"))
        EbxmlEnvelope._add_flag_if_present(extracted_values, ACK_REQUESTED,
                                           EbxmlEnvelope._extract_ebxml_value(xml_tree, "AckRequested"))
        EbxmlEnvelope._extract_attribute(xml_tree, "AckRequested", SOAP_NAMESPACE, "actor", extracted_values,
                                         ACK_SOAP_ACTOR)

        return extracted_values

    @staticmethod
    def _path_to_ebxml_element(name, parent=None):
        path = ".//"

        if parent is not None:
            path += EBXML_NAMESPACE + ":" + parent + "/"

        path += EBXML_NAMESPACE + ":" + name

        return path

    @staticmethod
    def _extract_ebxml_value(xml_tree, element_name, parent=None):
        xpath = EbxmlEnvelope._path_to_ebxml_element(element_name, parent=parent)
        return xml_tree.find(xpath, namespaces=NAMESPACES)

    @staticmethod
    def _extract_ebxml_text_value(xml_tree, element_name, parent=None):
        value = EbxmlEnvelope._extract_ebxml_value(xml_tree, element_name, parent)
        text = None

        if value is not None:
            text = value.text

        return text

    @staticmethod
    def _extract_attribute(xml_tree, element_name, attribute_namespace, attribute_name, values_dict, key):
        xpath = EbxmlEnvelope._path_to_ebxml_element(element_name)
        element = xml_tree.find(xpath, NAMESPACES)
        if element is not None:
            values_dict[key] = element.attrib["{" + NAMESPACES[attribute_namespace] + "}" + attribute_name]

    @staticmethod
    def _add_if_present(values_dict, key, value):
        if value is not None:
            values_dict[key] = value

    @staticmethod
    def _add_flag_if_present(values_dict, key, value):
        if value is not None:
            values_dict[key] = True
