import unittest

from edifact.outgoing.models.death.message_death import MessageSegmentDeathRegistrationDetails, \
    MessageSegmentDeathPatientDetails, DeathRegistrationMessage
from edifact.outgoing.models.interchange import Interchange
from edifact.outgoing.models.message import MessageBeginning, Messages


class TestInterchange(unittest.TestCase):
    """
    Test the generating of edifact interchange
    """

    def test_interchange_to_edifact(self):
        with self.subTest("When the transaction is to register a patient deduction (death)"):
            expected_edifact_interchange = ("UNB+UNOA:2+SNDR+RECP+190507:0900+00001++FHSREG'"
                                            "UNH+00001+FHSREG:0:1:FH:FHS001'"
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
                                            "UNT+14+00001'"
                                            "UNZ+1+00001'")

            msg_bgn = MessageBeginning(party_id="XX1", date_time="201905070900", ref_number="G5")
            msg_seg_reg_details = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                                         party_id="4826940,281",
                                                                         date_time="20190505",
                                                                         free_text="Died in Infinity Wars")

            msg_seg_pat_details = MessageSegmentDeathPatientDetails(id_number="N/10/10")

            msg = DeathRegistrationMessage(sequence_number="00001", message_beginning=msg_bgn,
                                           message_segment_registration_details=msg_seg_reg_details,
                                           message_segment_patient_details=msg_seg_pat_details)
            msgs = Messages([msg])

            interchange = Interchange(sender="SNDR", recipient="RECP", date_time="190507:0900", sequence_number="00001",
                                      messages=msgs).to_edifact()
            self.assertEqual(interchange, expected_edifact_interchange)
