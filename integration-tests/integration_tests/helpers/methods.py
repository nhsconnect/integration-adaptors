import os
from pathlib import Path
from test_definitions import ROOT_DIR

from utilities.file_utilities import FileUtilities
from integration_tests.helpers import interactions, xml_parser
from integration_tests.helpers.build_message import build_message


def get_asid():
    """ Looks up the asid from the environment settings

    The asid should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will read from 'asid.txt' (excluded from the repo)
        or default to '123456789012' if 'asid.txt' is not found
    """
    try:
        asid_file = str(Path(ROOT_DIR) / "data/certs/asid.txt")
        asid = FileUtilities.get_file_string(asid_file)
    except:
        asid = 123456789012

    return os.environ.get('ASID', os.environ.get('ASID', asid))


def get_mhs_inbound_queue():
    """ Looks up the mhs inbound hostname from the environment settings

    :return: the mhs inbound hostname

    The mhs inbound hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost:5672'
    """
    
    return os.environ.get('INBOUND_QUEUE_HOST', 'http://localhost:5672/')


def get_mhs_hostname():
    """ Looks up the mhs hostname from the environment settings

    The mhs hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_scr_adaptor_hostname():
    """ Looks up the scr adaptor hostname from the environment settings

    The scr adaptor hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
    return "http://" + os.environ.get('SCR_ADAPTOR_ADDRESS', 'localhost') + "/"


def get_interaction_from_template(type, template, nhs_number, payload,
                                  pass_message_id=False, pass_correlation_id=False):
    """ Sends the template to be rendered and passed on to the the MHS

    :param type: the message type (one of 'async express', 'async reliable', 'synchronous' or 'forward_reliable'
    :param template: the template name
    :param nhs_number: the NHS number for the test patient
    :param payload: the text to be sent on to SPINE
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :param pass_correlation_id: flag to indicate if we need to pass on the correlation ID
    :return: the response from the MHS
    """
    return interactions.process_request(template, get_asid(), nhs_number, payload, pass_message_id, pass_correlation_id)


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


def get_section(xml, attribute, section_name, parent=None):
    """ Extracts the data from an XML section
    
    :param xml: the message that we're checking
    :param attribute: the attribute we want
    :param section_name: the section we're looking for
    :param parent: ...and it's parent (optional)
    :return: the extracted data
    """
    parser = xml_parser.XmlMessageParser()
    returned_data = parser.parse_message(xml)
    value = parser.extract_hl7xml_text_value(returned_data, attribute, section_name, parent=parent)

    return value


def check_status_code(response, expected_code):
    """ Validates the response status code

    :param response: the response (from the 'post' request
    :param expected_code: the code we're expecting
    :return: True is they match, otherwise False
    """
    return response.status_code == expected_code
