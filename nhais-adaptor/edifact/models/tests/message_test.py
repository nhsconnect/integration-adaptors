import unittest
from edifact.models.message import MessageHeader, MessageBeginning, MessageSegmentTrigger1, MessageTrailer, Message


class MessageHeaderTest(unittest.TestCase):
    """
    Test the generating of a message header
    """

    def test_message_header_to_edifact(self):
        msg_hdr = MessageHeader(sequence_number="00001").to_edifact()
        self.assertEqual(msg_hdr, "UNH+00001+FHSREG:0:1:FH:FHS001'")


class MessageTrailerTest(unittest.TestCase):
    """
    Test the generating of a message trailer
    """

    def test_message_trailer_to_edifact(self):
        msg_trl = MessageTrailer(number_of_segments=5, sequence_number="00001").to_edifact()
        self.assertEqual(msg_trl, "UNT+5+00001'")


class MessageBeginningTest(unittest.TestCase):
    """
    Test the generating of a message beginning
    """

    def test_message_beginning_to_edifact(self):
        expected_edifact_msg_beginning = """BGM+++507'NAD+FHS+XX1:954'DTM+137:201904230900:203'RFF+950:G1'"""
        msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1").to_edifact()
        self.assertEqual(msg_bgn, expected_edifact_msg_beginning)


class MessageSegmentTrigger1Test(unittest.TestCase):
    """
    Test the generating of a message segment trigger 1
    """

    def test_message_segment_trigger_1_to_edifact(self):
        expected_edifact_message_trigger_1 = ("S01+1'"
            "RFF+TN:17'"
            "NAD+GP+4826940,281:900'"
            "HEA+ACD+A:ZZZ'"
            "HEA+ATP+1:ZZZ'"
            "DTM+956:20190423:102'"
            "LOC+950+BURY'")

        msg_trg_1 = MessageSegmentTrigger1(transaction_number=17,
                                           party_id="4826940,281",
                                           acceptance_code="A",
                                           acceptance_type="1",
                                           date_time="2019-04-23 09:00:04.159338",
                                           location="Bury").to_edifact()
        self.assertEqual(msg_trg_1, expected_edifact_message_trigger_1)


class MessageTest(unittest.TestCase):
    """
    Test the generating of a message
    """

    def test_message_to_edifact(self):
        expected_edifact_message = ("UNH+00001+FHSREG:0:1:FH:FHS001'"
            "BGM+++507'"
            "NAD+FHS+XX1:954'"
            "DTM+137:201904230900:203'"
            "RFF+950:G1'"
            "UNT+5+00001'")
        msg_hdr = MessageHeader(sequence_number="00001")
        msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")
        msg_trl = MessageTrailer(number_of_segments=5, sequence_number="00001")
        msg = Message(header=msg_hdr, message_beginning=msg_bgn, trailer=msg_trl).to_edifact()
        self.assertEqual(msg, expected_edifact_message)


if __name__ == '__main__':
    unittest.main()
