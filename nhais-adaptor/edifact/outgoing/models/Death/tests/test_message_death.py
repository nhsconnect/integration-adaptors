import unittest

from edifact.outgoing.models.Death.message_death import MessageSegmentDeathRegistrationDetails, \
    MessageSegmentDeathPatientDetails, MessageTypeDeath
from edifact.outgoing.models.message import MessageBeginning


class TestMessageDeath(unittest.TestCase):
    """
    Test the generating of a message segment of registration information
    """

    def test_message_segment_registration_details_to_edifact(self):
        with self.subTest("For death registrations with free texts"):
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

        with self.subTest("For death registrations without free texts"):
            expected_edifact_message = ("S01+1'"
                                        "RFF+TN:17'"
                                        "NAD+GP+4826940,281:900'"
                                        "GIS+1:ZZZ'"
                                        "DTM+961:20190423:102'")

            msg_seg_reg_details = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                                         party_id="4826940,281",
                                                                         date_time="2019-04-23 09:00:04.159338").to_edifact()
            self.assertEqual(msg_seg_reg_details, expected_edifact_message)

    def test_message_segment_patient_details_to_edifact(self):
        with self.subTest("For a death registration"):
            expected_edifact_message = ("S02+2'"
                                        "PNA+PAT+N/10/10:OPI'")

            msg_seg_pat_details = MessageSegmentDeathPatientDetails(id_number="N/10/10").to_edifact()
            self.assertEqual(msg_seg_pat_details, expected_edifact_message)

    def test_message_to_edifact(self):
        expected_edifact_message = ("UNH+00001+FHSREG:0:1:FH:FHS001'"
                                    "BGM+++507'"
                                    "NAD+FHS+XX1:954'"
                                    "DTM+137:201905070900:203'"
                                    "RFF+950:G5'"
                                    "S01+1'"
                                    "RFF+TN:17'"
                                    "NAD+GP+4826940,281:900'"
                                    "GIS+1:ZZZ'"
                                    "DTM+961:20190505:102'"
                                    "FTX+RGI+++DIED IN INFINITY WARS'"
                                    "S02+2'"
                                    "PNA+PAT+N/10/10:OPI'"
                                    "UNT+14+00001'")
        msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-05-07 09:00:04.159338", ref_number="G5")
        msg_seg_reg_details = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                                     party_id="4826940,281",
                                                                     date_time="2019-05-05 09:00:04.159338",
                                                                     free_text="Died in Infinity Wars")

        msg_seg_pat_details = MessageSegmentDeathPatientDetails(id_number="N/10/10")

        msg = MessageTypeDeath(sequence_number="00001", message_beginning=msg_bgn,
                               message_segment_registration_details=msg_seg_reg_details,
                               message_segment_patient_details=msg_seg_pat_details).to_edifact()
        self.assertEqual(msg, expected_edifact_message)

