import os
from pathlib import Path

from utilities.file_utilities import FileUtilities

from integration_tests.helpers import interactions, xml_parser
from integration_tests.helpers.build_message import build_message
from test_definitions import ROOT_DIR


def get_asid():
    """
    Looks up the asid from the environment settings
    :return: the asid

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


def get_mhs_hostname():
    """
    Looks up the mhs hostname from the environment settings
    :return: the mhs hostname

    The mhs hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_scr_adaptor_hostname():
<<<<<<< HEAD
=======
    """
    Looks up the scr adaptor hostname from the environment settings
    :return: the scr adaptor hostname

    The scr adaptor hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
    return "http://" + os.environ.get('SCR_ADAPTOR_ADDRESS', 'localhost') + "/"


def get_interaction_from_template(interaction_name, template, nhs_number, payload, pass_message_id=False):
>>>>>>> minor refactoring
    """
    Looks up the scr adaptor hostname from the environment settings
    :return: the scr adaptor hostname

    The scr adaptor hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
<<<<<<< HEAD
    return "http://" + os.environ.get('SCR_ADAPTOR_ADDRESS', 'localhost') + "/"


def get_interaction_from_template(interaction_name, nhs_number, payload, pass_message_id=False):
    """
    Sends the template to bo rendered and passed on to the the MHS
    :param interaction_name: the type of message (also the template name)
    :param nhs_number: the NHS number for the test patient
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :return: the response from the MHS
    """
    return interactions.process_request(interaction_name, get_asid(), nhs_number, payload,
                                        pass_message_id=pass_message_id)


=======
    return interactions.process_request(interaction_name, template, get_asid(), nhs_number, payload,
                                        pass_message_id=pass_message_id)


>>>>>>> minor refactoring
def get_json(template, patient_nhs_number, payload):
    """
    renders the template
    :param template: the template to use
    :param patient_nhs_number: the NHS number of the test patient
    :return: populated template xml string
    """
    return build_message(template, get_asid(), patient_nhs_number, payload)


def check_response(returned_xml):
    """
    Validates the given XML contains a 'requestSuccessDetail' section
    :param returned_xml: the message that we're checking
    :return: True if section is present, otherwise False
    """
    parser = xml_parser.XmlMessageParser()
    returned_data = parser.parse_message(returned_xml)
    value = parser.extract_hl7xml_value(returned_data, 'requestSuccessDetail')

    return value is not None
