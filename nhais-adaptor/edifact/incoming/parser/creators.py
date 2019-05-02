from edifact.incoming.models.interchange import InterchangeHeader
from edifact.incoming.models.message import MessageSegmentRegistrationDetails, MessageSegmentBeginningDetails

terminating_config = {
    "UNB": ["UNH"],
    "BGM": ["S01"],
    "S01": ["S02", "UNT"]
}


def determine_sgm_size(bigger_dict, starting_pos, trigger_key):
    new_dict = []

    for (k, v) in bigger_dict[starting_pos:]:
        if k not in terminating_config[trigger_key]:
            new_dict.append((k, v))
        else:
            break

    return new_dict


def create_interchange_header(interchange_header_dict):
    """
    Creates an incoming interchange header from the interchange header dictionary
    Since the interchange header details are all in the one line we extract the details
    from here
    :param interchange_header_dict: Will just be a list of 1
    containing a key value tuple of the interchange header details
    :return: InterchangeHeader: The incoming representation of the edifact interchange header
    """
    header_segment = interchange_header_dict[0]
    header_segment_value = header_segment[1]
    header_segment_values = header_segment_value.split("+")
    sender = header_segment_values[1]
    recipient = header_segment_values[2]
    date_time = header_segment_values[3]
    return InterchangeHeader(sender, recipient, date_time)


def create_message_segment_beginning(message_beginning_dict):
    """
    Creates an incoming message beginning from the message beginning dictionary
    :param message_beginning_dict: The dictionary will contain a list of lines relevant to the message beginning section
    :return: MessageSegmentBeginningDetails: The incoming representation of the edifact message beginning details
    """
    reference_segment = [value for key, value in message_beginning_dict if key == "RFF"][0]
    reference_values = reference_segment.split(":")
    reference_number = reference_values[1]
    return MessageSegmentBeginningDetails(reference_number)


def create_message_segment_registration(message_registration_dict):
    """
    Creates an incoming message registration from the message registration dictionary
    :param message_registration_dict: The dictionary will contain a list of lines relevant to the
    message registration section
    :return: MessageSegmentRegistrationDetails: The incoming representation of the edifact message registration details
    """
    transaction_segment = [value for key, value in message_registration_dict if key == "RFF"][0]
    transaction_values = transaction_segment.split(":")
    transaction_number = transaction_values[1]
    return MessageSegmentRegistrationDetails(transaction_number)

