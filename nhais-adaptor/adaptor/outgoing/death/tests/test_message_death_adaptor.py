import unittest

from testfixtures import compare

import adaptor.outgoing.death.message_death_adaptor as message_adaptor
import adaptor.outgoing.death.tests.fixtures as fixtures
from edifact.outgoing.models.death.message_death import MessageSegmentDeathPatientDetails, \
    MessageSegmentDeathRegistrationDetails


class TestMessageDeathAdaptor(unittest.TestCase):

    def test_create_message_segment_patient_details(self):
        expected = MessageSegmentDeathPatientDetails(id_number="NHSNO22222").segments

        op_def = fixtures.create_operation_definition_for_death_registration()

        msg_seg_pat_details = message_adaptor.create_message_segment_patient_detail(op_def).segments

        compare(msg_seg_pat_details, expected)

    def test_create_message_segment_registration_details(self):
        with self.subTest("Patient death registration details without free text"):
            expected = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                              party_id="4826940,281",
                                                              date_time="2019-04-20 09:00:04.15933").segments

            op_def = fixtures.create_operation_definition_for_death_registration()

            msg_seg_reg_details = message_adaptor.create_message_segment_registration_details(op_def).segments

            compare(msg_seg_reg_details, expected)

        with self.subTest("Patient death registration details with free text"):
            expected = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                              party_id="4826940,281",
                                                              date_time="2019-04-20 09:00:04.159338",
                                                              free_text="Died Happy").segments

            op_def = fixtures.create_operation_definition_for_death_registration(free_text="Died Happy")

            msg_seg_reg_details = message_adaptor.create_message_segment_registration_details(op_def).segments

            compare(msg_seg_reg_details, expected)
