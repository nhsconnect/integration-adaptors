"""Module containing methodology for populating a Gp Summary Upload template"""
import json
from pathlib import Path
from builder.pystache_message_builder import PystacheMessageBuilder

from scr_definitions import ROOT_DIR


class GpSummaryUpload(object):
    """Class for populating a Gp Summary Upload template"""

    summaryCareRecordPath = Path(ROOT_DIR) / "data/templates"
    file_name = "16UK05"
    interaction_id = "REPC_IN150016UK05"

    def __init__(self):
        self.builder = PystacheMessageBuilder(str(self.summaryCareRecordPath), self.file_name)

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
