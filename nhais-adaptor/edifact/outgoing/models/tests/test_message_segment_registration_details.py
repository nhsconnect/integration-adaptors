import unittest

from edifact.outgoing.models.message_segment_registration_details import MessageSegmentBirthRegistrationDetails, \
    MessageSegmentDeathRegistrationDetails


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
