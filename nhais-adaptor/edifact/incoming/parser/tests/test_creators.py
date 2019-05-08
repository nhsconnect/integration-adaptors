import unittest
from testfixtures import compare
import edifact.incoming.parser.creators as creators
from edifact.incoming.models.message import MessageSegmentRegistrationDetails, MessageSegmentBeginningDetails, \
    MessageSegmentPatientDetails
from edifact.incoming.models.interchange import InterchangeHeader
from edifact.incoming.parser import EdifactDict


class TestCreators(unittest.TestCase):

    def test_get_value_in_dict(self):
        with self.subTest("When there are no duplicate keys in the dictionary"):
            expected = "VALUE+CCC"

            dict_to_search = EdifactDict([
                ("AAA", "VALUE+AAA"),
                ("BBB", "VALUE+BBB"),
                ("CCC", "VALUE+CCC"),
                ("DDD", "VALUE+DDD")
            ])
            key_to_find = "CCC"
            result = creators.get_value_in_dict(dict_to_search, key_to_find)

            self.assertEqual(result, expected)

        with self.subTest("When there are duplicate keys in the dictionary returns the value of the first find"):
            expected = "VALUE+BBB"

            dict_with_duplicate_keys = EdifactDict([
                ("AAA", "VALUE+AAA"),
                ("BBB", "VALUE+BBB"),
                ("CCC", "VALUE+CCC"),
                ("BBB", "VALUE+BBB+1")
            ])
            key_to_find = "BBB"
            result = creators.get_value_in_dict(dict_with_duplicate_keys, key_to_find)

            self.assertEqual(result, expected)

    def test_create_interchange_header(self):
        expected = InterchangeHeader("SO01", "ROO5", "190429:1756")

        interchange_header_dict = EdifactDict([
            ("UNB", "UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS")
        ])
        interchange_header = creators.create_interchange_header(interchange_header_dict)

        compare(interchange_header, expected)

    def test_create_message_segment_beginning(self):
        expected = MessageSegmentBeginningDetails("F4")

        message_beginning_dict = EdifactDict([
            ("BGM", "++507"),
            ("NAD", "FHS+SO:954"),
            ("DTM", "137:201904291755:203"),
            ("RFF", "950:F4")
        ])
        msg_sgm_bgn = creators.create_message_segment_beginning(message_beginning_dict)

        compare(msg_sgm_bgn, expected)

    def test_create_message_segment_registration(self):
        expected = MessageSegmentRegistrationDetails("211102")

        message_registration_dict = EdifactDict([
            ("S01", "1"),
            ("RFF", "TN:211102"),
            ("NAD", "GP+1231231,PLP348:900")
        ])
        msg_sgm_reg = creators.create_message_segment_registration(message_registration_dict)

        compare(msg_sgm_reg, expected)

    def test_create_message_segment_patient(self):
        expected = MessageSegmentPatientDetails("9876556789")

        message_patient_dict = EdifactDict([
            ("S02", "2"),
            ("PNA", "PAT+9876556789:OPI"),
        ])
        msg_sgm_pat = creators.create_message_segment_patient(message_patient_dict)

        compare(msg_sgm_pat, expected)

