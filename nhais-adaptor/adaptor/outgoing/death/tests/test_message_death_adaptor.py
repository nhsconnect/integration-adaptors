import unittest

from testfixtures import compare

import adaptor.outgoing.death.tests.fixtures as fixtures
from adaptor.outgoing.death.message_death_adaptor import MessageDeathAdaptor
from edifact.outgoing.models.death.message_death import MessageSegmentDeathPatientDetails, \
    MessageSegmentDeathRegistrationDetails, DeathRegistrationMessage
from edifact.outgoing.models.message import MessageBeginning


class TestMessageDeathAdaptor(unittest.TestCase):

    def test_create_message_beginning(self):
        """
        Test the function to create an edifact section representing the beginning of a message
        """
        with self.subTest("Message beginning for a death registration"):
            expected = MessageBeginning(party_id="XX1", date_time="201904230900",
                                        ref_number="G5").segments

            op_def = fixtures.create_operation_definition_for_death_registration()

            message_adaptor = MessageDeathAdaptor(fhir_operation=op_def)
            msg_bgn = message_adaptor.create_message_beginning().segments

            compare(msg_bgn, expected)

    def test_create_message_segment_patient_details(self):
        expected = MessageSegmentDeathPatientDetails(id_number="NHSNO22222").segments

        op_def = fixtures.create_operation_definition_for_death_registration()

        message_adaptor = MessageDeathAdaptor(fhir_operation=op_def)
        msg_seg_pat_details = message_adaptor.create_message_segment_patient_detail().segments

        compare(msg_seg_pat_details, expected)

    def test_create_message_segment_registration_details(self):
        with self.subTest("Patient death registration details without free text"):
            expected = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                              party_id="4826940,281",
                                                              date_time="20190420").segments

            op_def = fixtures.create_operation_definition_for_death_registration()

            message_adaptor = MessageDeathAdaptor(fhir_operation=op_def)
            msg_seg_reg_details = message_adaptor.create_message_segment_registration_details().segments

            compare(msg_seg_reg_details, expected)

        with self.subTest("Patient death registration details with free text"):
            expected = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                              party_id="4826940,281",
                                                              date_time="20190420",
                                                              free_text="Died Happy").segments

            op_def = fixtures.create_operation_definition_for_death_registration(free_text="Died Happy")

            message_adaptor = MessageDeathAdaptor(fhir_operation=op_def)
            msg_seg_reg_details = message_adaptor.create_message_segment_registration_details().segments

            compare(msg_seg_reg_details, expected)

    def test_create_message(self):
        """
        Test the function to create an edifact message
        """
        with self.subTest("Death Registration"):
            msg_bgn = MessageBeginning(party_id="XX1", date_time="201904230900", ref_number="G5")
            msg_seg_pat_details = MessageSegmentDeathPatientDetails(id_number="NHSNO22222")
            msg_seg_reg_details = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                                         party_id="4826940,281",
                                                                         date_time="2019-04-20 09:00:04.159338")
            expected = DeathRegistrationMessage(sequence_number="000001", message_beginning=msg_bgn,
                                                message_segment_registration_details=msg_seg_reg_details,
                                                message_segment_patient_details=msg_seg_pat_details).segments

            op_def = fixtures.create_operation_definition_for_death_registration()

            message_adaptor = MessageDeathAdaptor(fhir_operation=op_def)
            message = message_adaptor.create_message().segments

            compare(message, expected)
