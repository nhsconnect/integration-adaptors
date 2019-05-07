import unittest
from edifact.outgoing.models.message import MessageHeader, MessageBeginning, MessageSegmentBirthRegistrationDetails, \
    MessageSegmentPatientDetails, MessageSegmentDeathRegistrationDetails, MessageTrailer, Message
from edifact.outgoing.models.name import Name
from edifact.outgoing.models.address import Address


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


class TestMessageSegmentRegistrationDetails(unittest.TestCase):
    """
    Test the generating of a message segment of registration information
    """

    def test_message_segment_registration_details_to_edifact(self):
        with self.subTest("For birth registrations"):
            expected_edifact_message = ("S01+1'"
                                        "RFF+TN:17'"
                                        "NAD+GP+4826940,281:900'"
                                        "HEA+ACD+A:ZZZ'"
                                        "HEA+ATP+1:ZZZ'"
                                        "DTM+956:20190423:102'"
                                        "LOC+950+BURY'")

            msg_seg_reg_details = MessageSegmentBirthRegistrationDetails(transaction_number=17,
                                                                         party_id="4826940,281",
                                                                         acceptance_code="A",
                                                                         acceptance_type="1",
                                                                         date_time="2019-04-23 09:00:04.159338",
                                                                         location="Bury").to_edifact()
            self.assertEqual(msg_seg_reg_details, expected_edifact_message)

        with self.subTest("For death registrations"):
            expected_edifact_message = ("S01+1'"
                                        "RFF+TN:17'"
                                        "NAD+GP+4826940,281:900'"
                                        "GIS+1:ZZZ'"
                                        "DTM+961:20190423:102'"
                                        "FTX+RGI+++DIED IN INFINITY WARS'")

            msg_seg_reg_details = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                                         party_id="4826940,281",
                                                                         date_time="2019-04-23 09:00:04.159338",
                                                                         free_text="Died in Infinity Wars").to_edifact()
            self.assertEqual(msg_seg_reg_details, expected_edifact_message)


class TestMessageSegmentPatientDetails(unittest.TestCase):
    """
    Test the generating of a message segment trigger 2
    """

    def test_message_segment_patient_details_to_edifact(self):
        expected_edifact_message = ("S02+2'"
                                    "PNA+PAT+N/10/10:OPI+++SU:STEVENS+FO:CHARLES+TI:MR+MI:ANTHONY+FS:JOHN'"
                                    "DTM+329:20190420:102'"
                                    "PDI+1'"
                                    "NAD+PAT++MOORSIDE FARM:OLD LANE:ST PAULS CRAY:ORPINGTON:KENT+++++BR6 7EW'")

        patient_name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr", middle_name="Anthony",
                            third_given_forename="John")
        patient_address = Address(house_name="MOORSIDE FARM", address_line_1="OLD LANE",
                                  address_line_2="ST PAULS CRAY", town="ORPINGTON", county="KENT", post_code="BR6 7EW")

        msg_seg_pat_details = MessageSegmentPatientDetails(id_number="N/10/10", name=patient_name,
                                                           date_of_birth="2019-04-20",
                                                           gender="1", address=patient_address).to_edifact()
        self.assertEqual(msg_seg_pat_details, expected_edifact_message)


class TestMessage(unittest.TestCase):
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
                                    "UNT+18+00001'")
        msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")
        msg_seg_reg_details = MessageSegmentBirthRegistrationDetails(transaction_number=17,
                                                                     party_id="4826940,281",
                                                                     acceptance_code="A",
                                                                     acceptance_type="1",
                                                                     date_time="2019-04-23 09:00:04.159338",
                                                                     location="Bury")
        patient_name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr", middle_name="Anthony",
                            third_given_forename="John")
        patient_address = Address(house_name="MOORSIDE FARM", address_line_1="OLD LANE",
                                  address_line_2="ST PAULS CRAY", town="ORPINGTON", county="KENT", post_code="BR6 7EW")

        msg_seg_pat_details = MessageSegmentPatientDetails(id_number="N/10/10", name=patient_name,
                                                           date_of_birth="2019-04-20",
                                                           gender="1", address=patient_address)

        msg = Message(sequence_number="00001", message_beginning=msg_bgn,
                      message_segment_registration_details=msg_seg_reg_details,
                      message_segment_patient_details=msg_seg_pat_details).to_edifact()
        self.assertEqual(msg, expected_edifact_message)
