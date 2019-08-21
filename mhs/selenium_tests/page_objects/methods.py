import os

from page_objects import interactions, xml_parser

HUMAN_READABLE = 'Payload stuff'


def get_asid():
    """
    The asid should be set in the 'Environment variables' section of the Run/Debug Configurations
    ...if this is not set, it will default to None (which will cause test failures!)
    """
    return os.environ.get('ASID', None)


def get_hostname():
    """
    The hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
    ...if this is not set, it will default to 'localhost'
    """
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_interaction(interaction_name, nhs_number, pass_message_id=False):
    return interactions.process_request(interaction_name, get_asid(), nhs_number, HUMAN_READABLE,
                                        pass_message_id=pass_message_id)


def get_log_timestamp(log_line):
    # the format of the log file is timestamp - level: details
    # the timestamp is in yyyy-mm-ddThh:mm:ss.ffffff format, so just return the first 26 chars
    return log_line[:26]


def get_log_level(log_line):
    # the format of the log file is timestamp - level: details
    # start by removing the timestamp and ' - '
    line = log_line[29:].split(':', 1)
    # then return upto the ':'
    return line[0]


def get_log_description(log_line):
    # the format of the log file is timestamp - level: details
    # start by removing the timestamp and ' - '
    line = log_line[29:].split(':', 1)
    # then return after the ':', stripping the end of line character
    return line[1].rstrip('\n')


def check_scr_response(returned_xml):
    parser = xml_parser.XmlMessageParser()
    returned_data = parser.parse_message(returned_xml)
    value = parser.extract_hl7xml_value(returned_data, 'requestSuccessDetail')

    return value is not None
