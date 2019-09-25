import os
from pathlib import Path

from utilities.file_utilities import FileUtilities

from integration_tests.helpers import interactions, xml_parser
from integration_tests.helpers.build_message import build_message
from test_definitions import ROOT_DIR


def get_asid():
    """ Looks up the asid from the environment settings

    The asid should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will read from 'asid.txt' (excluded from the repo)
        or default to '123456789012' if 'asid.txt' is not found
    """
    try:
        asid_file = str(Path(ROOT_DIR) / "integration_tests/data/certs/asid.txt")
        asid = FileUtilities.get_file_string(asid_file)
    except:
        asid = None

    return os.environ.get('INTEGRATION_TEST_ASID', asid)


def get_mhs_hostname():
    """ Looks up the mhs hostname from the environment settings

    The mhs hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_json(template, patient_nhs_number, payload):
    """ Renders the template

    :param template: the template to use
    :param patient_nhs_number: the NHS number of the test patient
    :param payload: the actual payload message being inserted into the template
    """
    return build_message(template, get_asid(), patient_nhs_number, payload)


def check_response(returned_xml, section_name):
    """ Validates the given XML contains a given section

    :param returned_xml: the message that we're checking
    :param section_name: the section we're expecting
    :return: True if section is present, otherwise False
    """
    parser = xml_parser.XmlMessageParser()
    returned_data = parser.parse_message(returned_xml)
    section = parser.extract_hl7xml_section(returned_data, section_name)

    return section is not None
