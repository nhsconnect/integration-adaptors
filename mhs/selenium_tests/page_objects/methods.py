import os

from page_objects import interactions, xml_parser

HUMAN_READABLE = 'Payload stuff'


def get_asid():
    # The asid should be set in the 'Environment variables' section of the Run/Debug Configurations
    # ...if this is not set, it will default to '123456789012', which will cause test failures!)
    return os.environ.get('ASID', os.environ.get('ASID', 123456789012))


def get_hostname():
    # The hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
    # ...if this is not set, it will default to 'localhost'
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_interaction(interaction_name, nhs_number, pass_message_id=False):
    return interactions.process_request(interaction_name, get_asid(), nhs_number, HUMAN_READABLE,
                                        pass_message_id=pass_message_id)


def check_scr_response(returned_xml):
    parser = xml_parser.XmlMessageParser()
    returned_data = parser.parse_message(returned_xml)
    value = parser.extract_hl7xml_value(returned_data, 'requestSuccessDetail')

    return value is not None
