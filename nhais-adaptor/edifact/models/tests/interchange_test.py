import unittest
from edifact.models.interchange import Interchange, InterchangeHeader, InterchangeTrailer


class InterchangeHeaderTest(unittest.TestCase):
    """
    Test the generating of an interchange header
    """

    def test_interchange_header_to_edifact(self):
        int_hdr = InterchangeHeader(sender="SNDR", recipient="RECP", date_time="2019-04-23 09:00:04.159338", sequence_number="00001").to_edifact()
        self.assertEqual(int_hdr, "UNB+UNOA:2+SNDR+RECP+190423:0900+00001'")


class InterchangeTrailerTest(unittest.TestCase):
    """
    Test the generating of an interchange trailer
    """

    def test_interchange_trailer_to_edifact(self):
        int_trl = InterchangeTrailer(number_of_messages=1, sequence_number="00001").to_edifact()
        self.assertEqual(int_trl, "UNZ+1+00001'")


class InterchangeTest(unittest.TestCase):
    """
    Test the generating of edifact message
    """
    def test_interchange_header_edifact(self):
        int_hdr = InterchangeHeader(sender="SNDR", recipient="RECP", date_time="2019-04-23 09:00:04.159338", sequence_number="00001")
        int_trl = InterchangeTrailer(number_of_messages=1, sequence_number="00001")
        interchange = Interchange(header=int_hdr, trailer=int_trl).to_edifact()
        self.assertEqual(interchange, "UNB+UNOA:2+SNDR+RECP+190423:0900+00001'UNZ+1+00001'")


if __name__ == '__main__':
    unittest.main()

