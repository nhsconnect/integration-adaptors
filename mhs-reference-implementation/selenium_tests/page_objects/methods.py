import os
from pathlib import Path

from definitions import ROOT_DIR
from selenium_tests.page_objects import interactions, xml_parser

HUMAN_READABLE = 'Payload stuff'
DATA_PATH = 'selenium_tests/data'


def get_asid():
    # The asid should be set in the 'Environment variables' section of the Run/Debug Configurations
    # ...if this is not set, it will be taken from data\local_asid file (which is excluded from GIT)
    return os.environ.get('ASID', os.environ.get('ASID', 1234567890))


def get_hostname():
    # The hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
    # ...if this is not set, it will default to 'http://localhost/'
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_interaction(interaction_name, nhs_number):
    return interactions.process_request(interaction_name, get_asid(), nhs_number, HUMAN_READABLE)


def check_scr_response(returned_xml):
    parser = xml_parser.XmlMessageParser()
    returned_data = parser.parse_message(returned_xml)
    value = parser.extract_hl7xml_value(returned_data, 'requestSuccessDetail')

    return value is not None
