import unittest
from testfixtures import compare
import edifact.incoming.message as message_parser
from edifact.incoming.message import MessageSegmentRegistrationDetails


class TestMessage(unittest.TestCase):

    def test_determine_sgm_size(self):
        expected = [
            ("S01", "+1"),
            ("RFF", "SOMETHING"),
            ("AND", "THIS"),
        ]

        bigger_dict = [
            ("AAA", "AAAAAAAAAAAA"),
            ("AAA", "AAAAAAAAAAAA"),
            ("S01", "+1"),
            ("RFF", "SOMETHING"),
            ("AND", "THIS"),
            ("S02", "+2"),
            ("AAA", "AAAAAAAAAAAA")
        ]

        result = message_parser.determine_sgm_size(bigger_dict, 2, "S01")

        compare(result, expected)

    def test_parse_message_segment_registration_details(self):
        expected = MessageSegmentRegistrationDetails("211102")

        something_dict = [
            ("S01", "+1"),
            ("RFF", "+TN:211102"),
            ("NAD", "+GP+1231231,PLP348:900")
        ]

        result = message_parser.parse_message_segment_registration(something_dict)

        compare(result, expected)
