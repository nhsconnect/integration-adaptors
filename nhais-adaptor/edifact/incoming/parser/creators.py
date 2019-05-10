from edifact.incoming.models.interchange import InterchangeHeader
from edifact.incoming.models.message import MessageSegmentRegistrationDetails, MessageSegmentBeginningDetails, \
    MessageSegmentPatientDetails
from edifact.incoming.parser import EdifactDict

SECTION_SEPARATOR = "+"
SUB_SECTION_SEPARATOR = ":"


def get_value_in_dict(dict_to_search: EdifactDict, key_to_find: str) -> str:
    """
    Extract the value segment out of the dictionary provided based upon the key. Will return the first result.
    :param dict_to_search: The dictionary of key value pairs.
    This is a list of tuples so need to loop through the dict.
    :param key_to_find: The key to find within the dict.
    :return: The Value as a string.
    """
    value = [value for key, value in dict_to_search if key == key_to_find][0]
    return value


def create_interchange_header(interchange_header_dict: EdifactDict) -> InterchangeHeader:
    """
    Creates an incoming interchange header from the interchange header dictionary.
    Since the interchange header details are all in the one line we extract the details
    from here.
    :param interchange_header_dict: Will just be a list of 1
    containing a key value tuple of the interchange header details.
    :return: InterchangeHeader: The incoming representation of the edifact interchange header.
    """
    header_segment = interchange_header_dict[0]
    header_segment_value = header_segment[1]
    header_segment_values = header_segment_value.split(SECTION_SEPARATOR)
    sender = header_segment_values[1]
    recipient = header_segment_values[2]
    date_time = header_segment_values[3]
    return InterchangeHeader(sender, recipient, date_time)


def create_message_segment_beginning(message_beginning_dict: EdifactDict) -> MessageSegmentBeginningDetails:
    """
    Creates an incoming message beginning from the message beginning dictionary.
    :param message_beginning_dict: The dictionary will contain a list of lines relevant to the
    message beginning section BGM.
    :return: MessageSegmentBeginningDetails: The incoming representation of the edifact message beginning details.
    """
    reference_segment = get_value_in_dict(dict_to_search=message_beginning_dict, key_to_find="RFF")
    reference_values = reference_segment.split(SUB_SECTION_SEPARATOR)
    reference_number = reference_values[1]
    return MessageSegmentBeginningDetails(reference_number)


def create_message_segment_registration(message_registration_dict: EdifactDict) -> MessageSegmentRegistrationDetails:
    """
    Creates an incoming message registration from the message registration dictionary.
    :param message_registration_dict: The dictionary will contain a list of lines relevant to the
    message registration section S01.
    :return: MessageSegmentRegistrationDetails: The incoming representation of the edifact message registration.
    """
    transaction_segment = get_value_in_dict(dict_to_search=message_registration_dict, key_to_find="RFF")
    transaction_values = transaction_segment.split(SUB_SECTION_SEPARATOR)
    transaction_number = transaction_values[1]
    return MessageSegmentRegistrationDetails(transaction_number)


def create_message_segment_patient(message_patient_dict: EdifactDict) -> MessageSegmentPatientDetails:
    """
    Creates an incoming message patient from the message message patient dictionary.
    :param message_patient_dict: The dictionary will contain a list of lines relevant to the
    message patient section S02.
    :return: MessageSegmentPatientDetails: The incoming representation of the edifact message patient.
    """
    patient_details_segment = get_value_in_dict(dict_to_search=message_patient_dict, key_to_find="PNA")
    patient_details_segment_values = patient_details_segment.replace(SUB_SECTION_SEPARATOR, SECTION_SEPARATOR).split(
        SECTION_SEPARATOR)
    nhs_number = patient_details_segment_values[1]
    return MessageSegmentPatientDetails(nhs_number)
