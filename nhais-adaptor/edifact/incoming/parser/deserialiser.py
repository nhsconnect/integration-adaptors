import edifact.incoming.parser.creators as parser
from edifact.incoming.models.message import MessageSegment
from edifact.incoming.models.interchange import Interchange


terminating_config = {
    "UNB": ["UNH"],
    "BGM": ["S01"],
    "S01": ["S02", "UNT"]
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


def convert_to_lines_two(lines):
    lines_two = []

    for line in lines:
        key_value = line.split("+", 1)
        lines_two.append((key_value[0], key_value[1]))

    return lines_two


def convert(lines):
    lines_two = convert_to_lines_two(lines)
    msgs = []
    interchange = None
    interchange_header = None
    msg_bgn_details = None
    msg_reg_details = None

    for index, line in enumerate(lines_two):
        key = line[0]

        if key == "UNB":
            interchange_header_line = extract_relevant_lines(lines_two, index, key)
            interchange_header = parser.create_interchange_header(interchange_header_line)

        elif key == "BGM":
            msg_bgn_lines = extract_relevant_lines(lines_two, index, key)
            msg_bgn_details = parser.create_message_segment_beginning(msg_bgn_lines)

        elif key == "S01":
            msg_reg_lines = extract_relevant_lines(lines_two, index, key)
            msg_reg_details = parser.create_message_segment_registration(msg_reg_lines)

        elif key == "UNT":
            msg = MessageSegment(msg_bgn_details, msg_reg_details)
            msgs.append(msg)

        elif key == "UNZ":
            interchange = Interchange(interchange_header, msgs)

    return interchange

