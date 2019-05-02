import unittest
from testfixtures import compare
import edifact.incoming.parser.creators as creators
from edifact.incoming.models.message import MessageSegmentRegistrationDetails, MessageSegmentBeginningDetails
from edifact.incoming.models.interchange import InterchangeHeader


class TestMessage(unittest.TestCase):

    def test_create_interchange_header(self):
        expected = InterchangeHeader("SO01", "ROO5", "190429:1756")

        interchange_header_dict = [
            ("UNB", "UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS")
        ]
        interchange_header = creators.create_interchange_header(interchange_header_dict)

        compare(interchange_header, expected)

    def test_create_message_segment_beginning(self):
        expected = MessageSegmentBeginningDetails("F4")

        message_beginning_dict = [
            ("BGM", "++507"),
            ("NAD", "FHS+SO:954"),
            ("DTM", "137:201904291755:203"),
            ("RFF", "950:F4")
        ]
        msg_sgm_bgn = creators.create_message_segment_beginning(message_beginning_dict)

        compare(msg_sgm_bgn, expected)

    def test_create_message_segment_registration(self):
        expected = MessageSegmentRegistrationDetails("211102")

        message_registration_dict = [
            ("S01", "1"),
            ("RFF", "TN:211102"),
            ("NAD", "GP+1231231,PLP348:900")
        ]
        msg_sgm_reg = creators.create_message_segment_registration(message_registration_dict)

        compare(msg_sgm_reg, expected)

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

        result = creators.determine_sgm_size(bigger_dict, 2, "S01")

        compare(result, expected)

    def test_parse_message_segment_registration_details(self):
        expected = MessageSegmentRegistrationDetails("211102")

        something_dict = [
            ("S01", "+1"),
            ("RFF", "+TN:211102"),
            ("NAD", "+GP+1231231,PLP348:900")
        ]

        result = creators.create_message_segment_registration(something_dict)

        compare(result, expected)
