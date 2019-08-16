import os
from pathlib import Path

from utilities.file_utilities import FileUtilities

from integration_tests.helpers import interactions, xml_parser
from integration_tests.helpers.build_scr import build_message
from test_definitions import ROOT_DIR

HUMAN_READABLE = 'Payload stuff'


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


def get_hostname():
    """
    Looks up the hostname from the environment settings
    :return: the hostname

    The hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_interaction_from_template(interaction_name, template, nhs_number, pass_message_id=False):
    """
    Sends the template to bo rendered and passed on to the the MHS
    :param interaction_name: the type of message
    :param template: the template to use
    :param nhs_number: the NHS number for the test patient
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :return: the response from the MHS
    """
    return interactions.process_request(interaction_name, template, get_asid(), nhs_number, HUMAN_READABLE,
                                        pass_message_id=pass_message_id)


def get_interaction_from_message(interaction_name, message):
    """
    Sends the message to bo rendered and passed on to the the MHS
    :param interaction_name: the type of message
    :param message: the message to be sent
    :return: the response from the MHS
    """
    return interactions.process_message(interaction_name, message)



def get_json(template, patient_nhs_number):
    """
    renders the template
    :param template: the template to use
    :param patient_nhs_number: the NHS number of the test patient
    :return: populated template xml string
    """
    return build_message(template, get_asid(), patient_nhs_number, HUMAN_READABLE)


def call_scr_adaptor(json_string):
    """
    Sends a json string the the SCR adaptor
    :param json_string: the json to be sent
    :return: the response from the adaptor
    """

    # TODO
    # once we know the scr_adaptor end point, we need to send the json_string to the scr_adaptor
        # return SummaryCareRecord().populate_template_with_json_string(json_string)
    # meanwhile, build an example response...
    # TEMPLATE_XML = 'xml_COPC_IN000001UK01'
    # TEMPLATE_XML = 'xml_QUPA_IN040000UK32'
    # TEMPLATE_XML = 'xml_QUPC_IN160101UK05'
    # TEMPLATE_XML = 'xml_REPC_IN150016UK05'
    scr_adaptor_response, message_id = build_message('xml_REPC_IN150016UK05', get_asid(), '9446245796', HUMAN_READABLE)
    return scr_adaptor_response


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
