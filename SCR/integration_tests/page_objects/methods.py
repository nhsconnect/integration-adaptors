import os

from integration_tests.page_objects import build_json, xml_parser
from scr.gp_summary_update import SummaryCareRecord

HUMAN_READABLE = 'Payload stuff'


def get_asid():
    # The asid should be set in the 'Environment variables' section of the Run/Debug Configurations
    # ...if this is not set, it will default to '123456789012', which will cause test failures!)
    return os.environ.get('ASID', os.environ.get('ASID', 123456789012))


def get_hostname():
    # The hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
    # ...if this is not set, it will default to 'localhost'
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_json(template, patient_nhs_number):
    return build_json.build_scr_json(template, get_asid(), patient_nhs_number, HUMAN_READABLE)


def call_scr_adaptor(json_string):
    """
    Parses a json string to a python dictionary and renders the template
    :param json_string:
    :return: populated template xml string
    """
    return SummaryCareRecord().populate_template_with_json_string(json_string)


def check_response(returned_xml):
    parser = xml_parser.XmlMessageParser()
    returned_data = parser.parse_message(returned_xml)
    value = parser.extract_hl7xml_value(returned_data, 'requestSuccessDetail')

    return value is not None
