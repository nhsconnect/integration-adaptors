import os
from pathlib import Path

from utilities.file_utilities import FileUtilities

from integration_tests.helpers import interactions, xml_parser
from integration_tests.helpers.build_scr import build_message
from test_definitions import ROOT_DIR

HUMAN_READABLE = 'Payload stuff'


def get_asid():
    # The asid should be set in the 'Environment variables' section of the Run/Debug Configurations
    # ...if this is not set, it will default to '123456789012', which will cause test failures!)
    return os.environ.get('ASID', os.environ.get('ASID', 123456789012))


def get_hostname():
    # The hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
    # ...if this is not set, it will default to 'localhost'
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_interaction(interaction_name, template, nhs_number, pass_message_id=False):
    return interactions.process_request(interaction_name, template, get_asid(), nhs_number, HUMAN_READABLE,
                                        pass_message_id=pass_message_id)


def get_json(template, patient_nhs_number):
    return build_message(template, get_asid(), patient_nhs_number, HUMAN_READABLE)


def call_scr_adaptor(json_string):
    """
    Parses a json string to a python dictionary and renders the template
    :param json_string:
    :return: populated template xml string
    """

    # TODO
    # once we know the scr_adaptor end point, we need to send the json_string to the scr_adaptor
    # meanwhile, use this example response...
    scr_adaptor_response = FileUtilities.get_file_string(
        str(Path(ROOT_DIR) / 'integration_tests/data/example_mhs_response.xml'))

    return scr_adaptor_response
    # return SummaryCareRecord().populate_template_with_json_string(json_string)


def check_response(returned_xml):
    parser = xml_parser.XmlMessageParser()
    returned_data = parser.parse_message(returned_xml)
    value = parser.extract_hl7xml_value(returned_data, 'requestSuccessDetail')

    return value is not None
