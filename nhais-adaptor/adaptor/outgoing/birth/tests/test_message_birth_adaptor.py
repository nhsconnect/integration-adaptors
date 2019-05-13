import unittest

from testfixtures import compare

from adaptor.outgoing.birth.message_birth_adaptor import MessageBirthAdaptor
import adaptor.outgoing.birth.tests.fixtures as fixtures
from edifact.outgoing.models.address import Address as EdifactAddress
from edifact.outgoing.models.birth.message_birth import MessageSegmentBirthPatientDetails, \
    MessageSegmentBirthRegistrationDetails, BirthRegistrationMessage
from edifact.outgoing.models.message import MessageBeginning
from edifact.outgoing.models.name import Name


class TestMessageBirthAdaptor(unittest.TestCase):

    def test_create_message_beginning(self):
        with self.subTest("Message beginning for a birth registration"):
            expected = MessageBeginning(party_id="XX1", date_time="201904230900",
                                        ref_number="G1").segments

            op_def = fixtures.create_operation_definition_for_birth_registration()

            message_adaptor = MessageBirthAdaptor(fhir_operation=op_def)
            msg_bgn = message_adaptor.create_message_beginning().segments

            compare(msg_bgn, expected)

    def test_create_message_segment_patient_details(self):
        with self.subTest("Patient with no previous names or addresses"):
            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            expected = MessageSegmentBirthPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                         date_of_birth="20190420",
                                                         gender="1", address=edifact_pat_address).segments

            op_def = fixtures.create_operation_definition_for_birth_registration()

            message_adaptor = MessageBirthAdaptor(fhir_operation=op_def)
            msg_seg_pat_details = message_adaptor.create_message_segment_patient_detail().segments

            compare(msg_seg_pat_details, expected)

    def test_create_message_segment_registration_details(self):
        with self.subTest("Patient registration details for type birth"):
            expected = MessageSegmentBirthRegistrationDetails(transaction_number=17, party_id="4826940,281",
                                                              date_time="20190423",
                                                              location="Spidey Town").segments

            op_def = fixtures.create_operation_definition_for_birth_registration()

            message_adaptor = MessageBirthAdaptor(fhir_operation=op_def)
            msg_seg_reg_details = message_adaptor.create_message_segment_registration_details().segments

            compare(msg_seg_reg_details, expected)

    def test_create_message(self):
        with self.subTest("Birth Registration"):
            msg_bgn = MessageBeginning(party_id="XX1", date_time="201904230900", ref_number="G1")
            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            msg_seg_pat_details = MessageSegmentBirthPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                                    date_of_birth="20190420",
                                                                    gender="1", address=edifact_pat_address)
            msg_seg_reg_details = MessageSegmentBirthRegistrationDetails(transaction_number=17, party_id="4826940,281",
                                                                         date_time="20190423",
                                                                         location="Spidey Town")
            expected = BirthRegistrationMessage(sequence_number="000001", message_beginning=msg_bgn,
                                                message_segment_registration_details=msg_seg_reg_details,
                                                message_segment_patient_details=msg_seg_pat_details).segments

            op_def = fixtures.create_operation_definition_for_birth_registration()

            message_adaptor = MessageBirthAdaptor(fhir_operation=op_def)
            message = message_adaptor.create_message().segments

            compare(message, expected)
