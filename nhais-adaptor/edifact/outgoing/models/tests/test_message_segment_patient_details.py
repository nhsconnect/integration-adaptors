import unittest

from edifact.outgoing.models.address import Address
from edifact.outgoing.models.message_segment_patient_details import MessageSegmentBirthPatientDetails, \
    MessageSegmentDeathPatientDetails
from edifact.outgoing.models.name import Name


class TestMessageSegmentPatientDetails(unittest.TestCase):
    """
    Test the generating of a message segment trigger 2
    """

    def test_message_segment_patient_details_to_edifact(self):
        with self.subTest("For a birth registration"):
            expected_edifact_message = ("S02+2'"
                                        "PNA+PAT+N/10/10:OPI+++SU:STEVENS+FO:CHARLES+TI:MR+MI:ANTHONY+FS:JOHN'"
                                        "DTM+329:20190420:102'"
                                        "PDI+1'"
                                        "NAD+PAT++MOORSIDE FARM:OLD LANE:ST PAULS CRAY:ORPINGTON:KENT+++++BR6 7EW'")

            patient_name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr",
                                middle_name="Anthony",
                                third_given_forename="John")
            patient_address = Address(house_name="MOORSIDE FARM", address_line_1="OLD LANE",
                                      address_line_2="ST PAULS CRAY", town="ORPINGTON", county="KENT",
                                      post_code="BR6 7EW")

            msg_seg_pat_details = MessageSegmentBirthPatientDetails(id_number="N/10/10", name=patient_name,
                                                                    date_of_birth="2019-04-20",
                                                                    gender="1", address=patient_address).to_edifact()
            self.assertEqual(msg_seg_pat_details, expected_edifact_message)

        with self.subTest("For a death registration"):
            expected_edifact_message = ("S02+2'"
                                        "PNA+PAT+N/10/10:OPI'")

            msg_seg_pat_details = MessageSegmentDeathPatientDetails(id_number="N/10/10").to_edifact()
            self.assertEqual(msg_seg_pat_details, expected_edifact_message)