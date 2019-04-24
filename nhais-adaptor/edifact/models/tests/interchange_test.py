import unittest
from edifact.models.interchange import Interchange, InterchangeHeader


class InterchangeHeaderTest(unittest.TestCase):
    """
    Test the generating of an interchange header
    """

    def test_interchange_header_to_edifact(self):
        int_hdr = InterchangeHeader(sender="SNDR", recipient="RECP", date_time="920113:1317", sequence_number="00001").to_edifact()
        self.assertEqual(int_hdr, "UNB+UNOA:2+SNDR+RECP+920113:1317+00001'")


class InterchangeTest(unittest.TestCase):
    """
    Test the generating of edifact message
    """
    def test_interchange_header_edifact(self):
        interchange = Interchange("header").to_edifact()
        self.assertEqual(interchange, "AAA-header")


if __name__ == '__main__':
    unittest.main()

