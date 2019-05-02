import unittest
import edifact.parser.breaker_new as breaker_new
from testfixtures import compare
from edifact.parser.message import MessageSegmentRegistrationDetails, MessageSegmentBeginningDetails, MessageSegment, \
    Interchange, InterchangeHeader, Messages


class TestBreakerNew(unittest.TestCase):

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

        result = breaker_new.convert(input_lines)
        compare(result, expected)
