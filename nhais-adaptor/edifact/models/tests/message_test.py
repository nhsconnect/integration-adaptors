import unittest
from edifact.models.message import MessageHeader, MessageBeginning, MessageSegmentTrigger1, MessageSegmentTrigger2, MessageTrailer, Message
from edifact.models.name import Name
from edifact.models.address import Address

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


class MessageSegmentTrigger2Test(unittest.TestCase):
    """
    Test the generating of a message segment trigger 2
    """

    def test_message_segment_trigger_2_to_edifact(self):
        expected_edifact_message_trigger_2 = ("S02+2'"
            "PNA+PAT+N/10/10:OPI+++SU:STEVENS+FO:CHARLES+TI:MR+MI:ANTHONY+FS:JOHN'"
            "DTM+329:20190420:102'"
            "PDI+1'"
            "NAD+PAT++MOORSIDE FARM:OLD LANE:ST PAULS CRAY:ORPINGTON:KENT+++++BR6 7EW'")

        patient_name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr", middle_name="Anthony", third_given_forename="John")
        patient_address = Address(house_name="MOORSIDE FARM", address_line_1="OLD LANE",
                                  address_line_2="ST PAULS CRAY", town="ORPINGTON", county="KENT", post_code="BR6 7EW")

        msg_trg_2 = MessageSegmentTrigger2(id_number="N/10/10", name=patient_name, date_of_birth="2019-04-20", gender="1", address=patient_address).to_edifact()
        self.assertEqual(msg_trg_2, expected_edifact_message_trigger_2)


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
            "S01+1'"
            "RFF+TN:17'"
            "NAD+GP+4826940,281:900'"
            "HEA+ACD+A:ZZZ'"
            "HEA+ATP+1:ZZZ'"
            "DTM+956:20190423:102'"
            "LOC+950+BURY'"
            "S02+2'"
            "PNA+PAT+N/10/10:OPI+++SU:STEVENS+FO:CHARLES+TI:MR+MI:ANTHONY+FS:JOHN'"
            "DTM+329:20190420:102'"
            "PDI+1'"
            "NAD+PAT++MOORSIDE FARM:OLD LANE:ST PAULS CRAY:ORPINGTON:KENT+++++BR6 7EW'"
            "UNT+5+00001'")
        msg_hdr = MessageHeader(sequence_number="00001")
        msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")
        msg_trg_1 = MessageSegmentTrigger1(transaction_number=17,
                                           party_id="4826940,281",
                                           acceptance_code="A",
                                           acceptance_type="1",
                                           date_time="2019-04-23 09:00:04.159338",
                                           location="Bury")
        patient_name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr", middle_name="Anthony", third_given_forename="John")
        patient_address = Address(house_name="MOORSIDE FARM", address_line_1="OLD LANE",
                                  address_line_2="ST PAULS CRAY", town="ORPINGTON", county="KENT", post_code="BR6 7EW")

        msg_trg_2 = MessageSegmentTrigger2(id_number="N/10/10", name=patient_name, date_of_birth="2019-04-20", gender="1", address=patient_address)
        msg_trl = MessageTrailer(number_of_segments=5, sequence_number="00001")
        msg = Message(header=msg_hdr, message_beginning=msg_bgn, message_segment_trigger_1=msg_trg_1, message_segment_trigger_2=msg_trg_2, trailer=msg_trl).to_edifact()
        self.assertEqual(msg, expected_edifact_message)


if __name__ == '__main__':
    unittest.main()
