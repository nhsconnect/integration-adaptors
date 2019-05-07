import unittest
from edifact.outgoing.models.interchange import Interchange, InterchangeHeader, InterchangeTrailer
from edifact.outgoing.models.message import MessageBeginning, MessageTypeBirth, Messages
from edifact.outgoing.models.message_segment_patient_details import MessageSegmentBirthPatientDetails
from edifact.outgoing.models.message_segment_registration_details import MessageSegmentBirthRegistrationDetails
from edifact.outgoing.models.name import Name
from edifact.outgoing.models.address import Address


class TestInterchangeHeader(unittest.TestCase):
    """
    Test the generating of an interchange header
    """

    def test_interchange_header_to_edifact(self):
        int_hdr = InterchangeHeader(sender="SNDR", recipient="RECP", date_time="2019-04-23 09:00:04.159338",
                                    sequence_number="00001").to_edifact()
        self.assertEqual(int_hdr, "UNB+UNOA:2+SNDR+RECP+190423:0900+00001++FHSREG'")


class TestInterchangeTrailer(unittest.TestCase):
    """
    Test the generating of an interchange trailer
    """

    def test_interchange_trailer_to_edifact(self):
        int_trl = InterchangeTrailer(number_of_messages=1, sequence_number="00001").to_edifact()
        self.assertEqual(int_trl, "UNZ+1+00001'")


class TestInterchange(unittest.TestCase):
    """
    Test the generating of edifact interchange
    """

    def test_interchange_to_edifact(self):
        with self.subTest("When the transaction is to register a patient birth"):
            expected_edifact_interchange = ("UNB+UNOA:2+SNDR+RECP+190423:0900+00001++FHSREG'"
                                            "UNH+00001+FHSREG:0:1:FH:FHS001'"
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
                                            "UNT+18+00001'"
                                            "UNZ+1+00001'")

            date_time = "2019-04-23 09:00:04.159338"

            msg_bgn = MessageBeginning(party_id="XX1", date_time=date_time, ref_number="G1")
            msg_seg_reg_details = MessageSegmentBirthRegistrationDetails(transaction_number=17,
                                                                         party_id="4826940,281",
                                                                         acceptance_code="A",
                                                                         acceptance_type="1",
                                                                         date_time="2019-04-23 09:00:04.159338",
                                                                         location="Bury")
            patient_name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr",
                                middle_name="Anthony",
                                third_given_forename="John")
            patient_address = Address(house_name="MOORSIDE FARM", address_line_1="OLD LANE",
                                      address_line_2="ST PAULS CRAY", town="ORPINGTON", county="KENT",
                                      post_code="BR6 7EW")

            msg_seg_pat_details = MessageSegmentBirthPatientDetails(id_number="N/10/10", name=patient_name,
                                                                    date_of_birth="2019-04-20",
                                                                    gender="1", address=patient_address)

            msg = MessageTypeBirth(sequence_number="00001", message_beginning=msg_bgn,
                                   message_segment_registration_details=msg_seg_reg_details,
                                   message_segment_patient_details=msg_seg_pat_details)
            msgs = Messages([msg])

            interchange = Interchange(sender="SNDR", recipient="RECP", date_time=date_time, sequence_number="00001",
                                      messages=msgs).to_edifact()
            self.assertEqual(interchange, expected_edifact_interchange)

        # with self.subTest("When the transaction is to register a patient deduction (death)"):
        #     expected_edifact_interchange = ("UNB+UNOA:2+TES5+XX11+920113:1317+00000002++FHSREG'"
        #                                     "UNH+00000003+FHSREG:0:1:FH:FHS001'"
        #                                     "BGM+++507'"
        #                                     "NAD+FHS+XX1:954'"
        #                                     "DTM+137:199201131317:203'"
        #                                     "RFF+950:G5'"
        #                                     "S01+1'"
        #                                     "RFF+TN:17'"
        #                                     "NAD+GP+4826940,281:900'"
        #                                     "GIS+1:ZZZ'"
        #                                     "DTM+961:19911225:102'"
        #                                     "FTX+RGI+++DIED ON HOLIDAY IN MAJORCA'"
        #                                     "S02+2'"
        #                                     "PNA+PAT+N/10/10:OPI'"
        #                                     "UNT+14+00000003'"
        #                                     "UNZ+1+00000002'")
        #
        #     date_time = "2019-05-07 09:00:04.159338"
        #
        #     msg_bgn = MessageBeginning(party_id="XX1", date_time=date_time, ref_number="G5")
        #     msg_seg_reg_details = MessageSegmentBirthRegistrationDetails(transaction_number=17,
        #                                                                  party_id="4826940,281",
        #                                                                  acceptance_code="A",
        #                                                                  acceptance_type="1",
        #                                                                  date_time="2019-04-23 09:00:04.159338",
        #                                                                  location="Bury")
        #     patient_name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr", middle_name="Anthony",
        #                         third_given_forename="John")
        #     patient_address = Address(house_name="MOORSIDE FARM", address_line_1="OLD LANE",
        #                               address_line_2="ST PAULS CRAY", town="ORPINGTON", county="KENT", post_code="BR6 7EW")
        #
        #     msg_seg_pat_details = MessageSegmentBirthPatientDetails(id_number="N/10/10", name=patient_name,
        #                                                        date_of_birth="2019-04-20",
        #                                                        gender="1", address=patient_address)
        #
        #     msg = Message(sequence_number="00001", message_beginning=msg_bgn,
        #                   message_segment_registration_details=msg_seg_reg_details,
        #                   message_segment_patient_details=msg_seg_pat_details)
        #     msgs = Messages([msg])
        #
        #     interchange = Interchange(sender="SNDR", recipient="RECP", date_time=date_time, sequence_number="00001",
        #                               messages=msgs).to_edifact()
        #     self.assertEqual(interchange, expected_edifact_interchange)
