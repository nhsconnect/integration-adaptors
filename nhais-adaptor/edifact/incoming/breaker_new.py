import edifact.incoming.message as parser
from edifact.incoming.models.message import MessageSegment
from edifact.incoming.models.interchange import Interchange


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
            interchange_header_line = parser.determine_sgm_size(lines_two, index, key)
            interchange_header = parser.parse_interchange_header(interchange_header_line)

        elif key == "BGM":
            msg_bgn_lines = parser.determine_sgm_size(lines_two, index, key)
            msg_bgn_details = parser.parse_message_segment_beginning(msg_bgn_lines)

        elif key == "S01":
            msg_reg_lines = parser.determine_sgm_size(lines_two, index, key)
            msg_reg_details = parser.parse_message_segment_registration(msg_reg_lines)

        elif key == "UNT":
            msg = MessageSegment(msg_bgn_details, msg_reg_details)
            msgs.append(msg)

        elif key == "UNZ":
            interchange = Interchange(interchange_header, msgs)

    return interchange


