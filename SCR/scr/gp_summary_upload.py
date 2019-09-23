"""Module containing methodology for populating a Gp Summary Upload template"""
import json
from pathlib import Path
from builder.pystache_message_builder import PystacheMessageBuilder
from scr_definitions import ROOT_DIR
from typing import Dict
import xml.etree.ElementTree as ET


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
        NOTE: This is purely a success parsing response mecahnism, error parsing is currently not supported
        :param response_message: A Successful Gp Summary Upload response acknolwedgement
        :return: A dictionary containing the key success details of the message
        """
        root = ET.ElementTree(ET.fromstring(response_message)).getroot()
        message_id = self._find_hl7_element(root, './/hl7:id').attrib['root']
        message_reference = self._find_hl7_element(root, './/hl7:messageRef/hl7:id').attrib['root']
        creation_time = self._find_hl7_element(root, './/hl7:creationTime').attrib['value']
        message_detail = self._find_hl7_element(root, './/hl7:ControlActEvent/hl7:requestSuccessDetail/hl7:detail').text
        return {
            'messageRef': message_reference,
            'messageId': message_id,
            'creationTime': creation_time,
            'messageDetail': message_detail
        }

    def _find_hl7_element(self, root, element_name:str):
        return root.find(element_name, namespaces={'hl7': 'urn:hl7-org:v3'})
