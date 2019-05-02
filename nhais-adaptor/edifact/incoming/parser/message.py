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


def parse_interchange_header(something_dict):
    """

    :param something_dict:
    :return:
    """
    header_segment = something_dict[0]
    header_segment_value = header_segment[1]
    header_segment_values = header_segment_value.split("+")
    sender = header_segment_values[1]
    recipient = header_segment_values[2]
    date_time = header_segment_values[3]
    return InterchangeHeader(sender, recipient, date_time)


def parse_message_segment_beginning(something_dict):
    """

    :param something_dict:
    :return:
    """
    reference_segment = [value for key, value in something_dict if key == "RFF"][0]
    reference_values = reference_segment.split(":")
    reference_number = reference_values[1]
    return MessageSegmentBeginningDetails(reference_number)


def parse_message_segment_registration(something_dict):
    """

    :param something_dict:
    :return:
    """
    transaction_segment = [value for key, value in something_dict if key == "RFF"][0]
    transaction_values = transaction_segment.split(":")
    transaction_number = transaction_values[1]
    return MessageSegmentRegistrationDetails(transaction_number)

