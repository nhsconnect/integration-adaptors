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


def get_mhs_inbound_queue_url():
    """ Looks up the mhs inbound host URL from the environment settings.

    :return: the mhs inbound host URL

    The mhs inbound hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost:5672'
    """
    return os.environ.get('MHS_INBOUND_QUEUE_URL', 'http://localhost:5672')


def get_mhs_inbound_queue_name():
    """ Looks up the mhs inbound queue name from the environment settings.

    :return: the mhs inbound queue name

    The mhs inbound queue name should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'inbound'
    """
    return os.environ.get('MHS_INBOUND_QUEUE_NAME', 'inbound')


def get_mhs_inbound_queue_certs():
    username = os.environ.get('MHS_SECRET_INBOUND_QUEUE_USERNAME', None)
    password = os.environ.get('MHS_SECRET_INBOUND_QUEUE_PASSWORD', None)
    return username, password


def get_mhs_hostname():
    """ Looks up the mhs hostname from the environment settings

    The mhs hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
    # TODO: Need to be able to use HTTPs as well as HTTP
    return "https://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_interaction_from_template(type, template, nhs_number, payload,
                                  pass_message_id=False, pass_correlation_id=False, sync_async=False):
    """ Sends the template to be rendered and passed on to the the MHS

    :param type: the message type (one of 'async express', 'async reliable', 'synchronous' or 'forward_reliable'
    :param template: the template name
    :param nhs_number: the NHS number for the test patient
    :param payload: the text to be sent on to SPINE
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :param pass_correlation_id: flag to indicate if we need to pass on the correlation ID
    :param sync_async: What the sync-async flag of the header should be set to
    :return: the response from the MHS
    """
    return interactions.process_request(template, get_asid(), nhs_number, payload, pass_message_id, pass_correlation_id,
                                        sync_async)


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
