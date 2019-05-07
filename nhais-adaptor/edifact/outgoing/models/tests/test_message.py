import unittest
from edifact.outgoing.models.message import MessageHeader, MessageBeginning, MessageTrailer


class TestMessageHeader(unittest.TestCase):
    """
    Test the generating of a message header
    """

    def test_message_header_to_edifact(self):
        msg_hdr = MessageHeader(sequence_number="00001").to_edifact()
        self.assertEqual(msg_hdr, "UNH+00001+FHSREG:0:1:FH:FHS001'")


class TestMessageTrailer(unittest.TestCase):
    """
    Test the generating of a message trailer
    """

    def test_message_trailer_to_edifact(self):
        msg_trl = MessageTrailer(number_of_segments=5, sequence_number="00001").to_edifact()
        self.assertEqual(msg_trl, "UNT+5+00001'")


class TestMessageBeginning(unittest.TestCase):
    """
    Test the generating of a message beginning
    """

    def test_message_beginning_to_edifact(self):
        expected_edifact_message = """BGM+++507'NAD+FHS+XX1:954'DTM+137:201904230900:203'RFF+950:G1'"""
        msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1").to_edifact()
        self.assertEqual(msg_bgn, expected_edifact_message)

