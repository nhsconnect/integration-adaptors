import unittest
import edifact.incoming.parser.deserialiser as deserialiser
from testfixtures import compare
from edifact.incoming.models.message import MessageSegmentRegistrationDetails, MessageSegmentBeginningDetails, \
    MessageSegment, Messages
from edifact.incoming.models.interchange import InterchangeHeader, Interchange


class TestBreakerNew(unittest.TestCase):

    def test_extract_relevant_lines(self):
        original_dict = [
            ("UNB", "UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS"),
            ("UNH", "00024986+FHSREG:0:1:FH:FHS001"),
            ("BGM", "++507"),
            ("NAD", "FHS+SO:954"),
            ("DTM", "137:201904291755:203"),
            ("RFF", "950:F4"),
            ("S01", "1"),
            ("RFF", "TN:211102"),
            ("NAD", "GP+1231231,PLP348:900"),
            ("UNT", "9+00024986"),
            ("UNZ", "1+00016288"),
        ]

        with self.subTest("When the trigger key is UNB (the interchange header)"):
            expected = [("UNB", "UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS")]

            interchange_header_dict = deserialiser.extract_relevant_lines(original_dict, 0, "UNB")

            compare(interchange_header_dict, expected)

        with self.subTest("When the trigger key is BGM (the message beginning section)"):
            expected = [
                ("BGM", "++507"),
                ("NAD", "FHS+SO:954"),
                ("DTM", "137:201904291755:203"),
                ("RFF", "950:F4")
            ]

            message_beginning_dict = deserialiser.extract_relevant_lines(original_dict, 2, "BGM")

            compare(message_beginning_dict, expected)

        with self.subTest("When the trigger key is S01 (the message registration section)"):
            expected = [
                ("S01", "1"),
                ("RFF", "TN:211102"),
                ("NAD", "GP+1231231,PLP348:900")
            ]

            message_registration_dict = deserialiser.extract_relevant_lines(original_dict, 6, "S01")

            compare(message_registration_dict, expected)

    def test_convert_to_dict(self):
        expected = [
            ("UNB", "UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS"),
            ("UNH", "00024986+FHSREG:0:1:FH:FHS001"),
            ("BGM", "++507")
        ]

        input_lines = [
            "UNB+UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS",
            "UNH+00024986+FHSREG:0:1:FH:FHS001",
            "BGM+++507"
        ]
        converted_dict = deserialiser.convert_to_dict(input_lines)

        compare(converted_dict, expected)

    def test_breaker_new(self):
        expected = Interchange(InterchangeHeader("SO01", "ROO5", "190429:1756"), Messages([
            MessageSegment(MessageSegmentBeginningDetails("F4"), MessageSegmentRegistrationDetails("211102"))
        ]))

        input_lines = [
            "UNB+UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS",
            "UNH+00024986+FHSREG:0:1:FH:FHS001",
            "BGM+++507",
            "NAD+FHS+SO:954",
            "DTM+137:201904291755:203",
            "RFF+950:F4",
            "S01+1",
            "RFF+TN:211102",
            "NAD+GP+1231231,PLP348:900",
            "UNT+9+00024986",
            "UNZ+1+00016288",
        ]

        result = deserialiser.convert(input_lines)
        compare(result, expected)
