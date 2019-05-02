import edifact.incoming.parser.creators as creators
from edifact.incoming.models.message import MessageSegment
from edifact.incoming.models.interchange import Interchange


terminating_config = {
    "UNB": ["UNH"],
    "BGM": ["S01"],
    "S01": ["S02", "UNT"],
    "S02": ["UNT"]
}


def extract_relevant_lines(original_dict, starting_pos, trigger_key):
    """
    From the original dict generate a smaller dict just containing the relevant lines based upon the trigger key
    will keep looping till the terminating key is found in the terminating config
    :param original_dict: The original larger dictionary
    :param starting_pos: The starting position to start the loop from.
    This is to prevent starting the loop from the start each time and be slightly more efficient
    :param trigger_key: The trigger key for this section that will be used to find what the
    terminating key for the section is
    :return: A smaller dictionary with just the relevant lines for the section
    """
    new_dict = []

    for (key, value) in original_dict[starting_pos:]:
        if key not in terminating_config[trigger_key]:
            new_dict.append((key, value))
        else:
            break

    return new_dict


def convert_to_dict(lines):
    """
    Takes the list of original edifact lines and converts to a dict
    :param lines: a list of string of the original edifact lines
    :return: A list of Tuple with the extracted key and value. Since the keys in the edifact interchange can
    contain duplicates a tuple is required here rather than a set
    """
    generated_dict = []

    for line in lines:
        key_value = line.split("+", 1)
        generated_dict.append((key_value[0], key_value[1]))

    return generated_dict


def convert(lines):
    """
    Takes the original list of edifact lines and converts to a deserialised representation.
    Only relevant information from the edifact message is extracted and populated in the models
    :param lines: A list of string of the edifact lines
    :return: Interchange: The incoming representation of the edifact interchange
    """
    original_dict = convert_to_dict(lines)
    msgs = []
    interchange = None
    interchange_header = None
    msg_bgn_details = None
    msg_reg_details = None
    msg_pat_details = None

    for index, line in enumerate(original_dict):
        key = line[0]

        if key == "UNB":
            interchange_header_line = extract_relevant_lines(original_dict, index, key)
            interchange_header = creators.create_interchange_header(interchange_header_line)

        elif key == "BGM":
            msg_bgn_lines = extract_relevant_lines(original_dict, index, key)
            msg_bgn_details = creators.create_message_segment_beginning(msg_bgn_lines)

        elif key == "S01":
            msg_reg_lines = extract_relevant_lines(original_dict, index, key)
            msg_reg_details = creators.create_message_segment_registration(msg_reg_lines)

        elif key == "S02":
            msg_pat_lines = extract_relevant_lines(original_dict, index, key)
            msg_pat_details = creators.create_message_segment_patient(msg_pat_lines)

        elif key == "UNT":
            msg = MessageSegment(msg_bgn_details, msg_reg_details, msg_pat_details)
            msgs.append(msg)

        elif key == "UNZ":
            interchange = Interchange(interchange_header, msgs)

    return interchange

