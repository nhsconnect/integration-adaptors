"""Module containing methodology for populating a Gp Summary Upload template"""
import json
from pathlib import Path
from builder.pystache_message_builder import PystacheMessageBuilder
from scr_definitions import ROOT_DIR
from typing import Dict, Optional, Callable
import xml.etree.ElementTree as ET
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


class GpSummaryUpload(object):
    """Class for populating a Gp Summary Upload template"""

    summaryCareRecordPath = Path(ROOT_DIR) / "data/templates"
    file_template_name = "16UK05"
    interaction_id = "REPC_IN150016UK05"

    def __init__(self):
        self.builder = PystacheMessageBuilder(str(self.summaryCareRecordPath), self.file_template_name)

    def populate_template_with_file(self, json_file):
        """
        Given a file path to a Json file, this method will parse the json and populate the template
        :param json_file:
        :return: populated template xml string
        """
        with open(json_file) as file:
            data = json.load(file)
            return self.populate_template(data)

    def populate_template_with_json_string(self, json_string):
        """
        Parses a json string to a python dictionary and renders the template
        :param json_string:
        :return: populated template xml string
        """
        data = json.loads(json_string)
        return self.populate_template(data)

    def populate_template(self, input_hash):
        """
        Given a python dictionary this method returns a xml string containing the populated template of the
        GP Summary Update template
        :param input_hash:
        :return: xml string containing populated template
        """
        return self.builder.build_message(input_hash)

    def parse_response(self, response_message: str) -> Dict:
        """
        Parses te key values of a given Gp summary Upload response into a dictionary.
        NOTE: This is purely a success parsing response mechanism, error parsing is currently not supported
        :param response_message: A Successful Gp Summary Upload response acknowledgement
        :return: A dictionary containing the key success details of the message
        """
        root = self._get_root(response_message)
        if not root:
            return {'error': 'Failed to parse response from xml provided'}

        message_id = self._find_hl7_element_attribute(root, './/hl7:id', 'root')
        message_reference = self._find_hl7_element_attribute(root, './/hl7:messageRef//hl7:id', 'root')
        creation_time = self._find_hl7_element_attribute(root, './/hl7:creationTime', 'value')
        message_detail = self._find_hl7_element_text(root,
                                                     './/hl7:ControlActEvent//hl7:requestSuccessDetail//hl7:detail')

        return self._create_response_dictionary(message_id, message_reference, creation_time, message_detail)

    def _get_root(self, message: str) -> Optional[ET.Element]:
        """
        Parses an xml string and returns the root element of that element tree
        :param message: xml input string
        :return: The root element of the element tree
        """
        try:
            return ET.ElementTree(ET.fromstring(message)).getroot()
        except ET.ParseError:
            logger.exception('Exception raised while creating XML object from string')
            return None

    def _find_hl7_element_attribute(self, root: ET.Element, element_name: str, attribute: str) -> Optional[str]:
        """
        Searches the tree with the given root node for an element with the element name, then looks for the given 
        attribute of that element
        :param root: The root of the element tree
        :param element_name: The element tag to search for
        :param attribute: the attribute on that given element
        :return: The value of the attribute on the element, if it exists
        """
        try:
            return self._get_element(root, element_name, lambda x: x.attrib[attribute])
        except KeyError:
            logger.info('Failed to find attribute on {element} {attribute}',
                        fparams={'element': element_name, 'attribute': attribute})
            return None

    def _find_hl7_element_text(self, root: ET.Element, element_name: str):
        """
        :param root: The root of the element tree to search 
        :param element_name:  the name of the element to look for
        :return: the text within the tags of the given element
        """
        return self._get_element(root, element_name, lambda x: x.text)

    def _get_element(self, root: ET.Element, element_name: str, func: Callable[[ET.Element], str]):
        """
        Searches for an element on the element tree of the given root, the passes the element to the found function
        :param root: Root element of the element tree
        :param element_name: element to search for
        :param func: function to call which processes the result of the element search
        :return: the result of the func call 
        """
        element = root.find(element_name, namespaces={'hl7': 'urn:hl7-org:v3'})
        if element is None:
            return None

        return func(element)

    def _create_response_dictionary(self, message_id: str, message_ref: str, creation_time: str, message_detail: str) \
            -> Dict:
        """
        Creates a success/error dictionary based on the given parameters
        :param message_id: 
        :param message_ref: 
        :param creation_time: 
        :param message_detail: 
        :return: A dict containing either the parsed values or the errror response
        """
        if all([message_id, message_ref, creation_time, message_detail]):
            return {
                'messageRef': message_ref,
                'messageId': message_id,
                'creationTime': creation_time,
                'messageDetail': message_detail
            }
        else:
            logger.error('Failed to parse all necessary elements from xml {message_id} {message_reference}'
                         ' {creation_time} {message_details}',
                         {
                             'message_id': message_id,
                             'message_reference': message_ref,
                             'creation_time': creation_time,
                             'message_details': message_detail
                          })
            return {'error': 'Failed to parse all the necessary elements from xml returned from MHS'}

