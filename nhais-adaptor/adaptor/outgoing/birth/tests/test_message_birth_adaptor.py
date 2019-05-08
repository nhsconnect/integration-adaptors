import unittest

from testfixtures import compare

import adaptor.outgoing.birth.message_birth_adaptor as message_adaptor
import adaptor.outgoing.birth.tests.fixtures as fixtures
from edifact.outgoing.models.address import Address as EdifactAddress
from edifact.outgoing.models.birth.message_birth import MessageSegmentBirthPatientDetails, \
    MessageSegmentBirthRegistrationDetails
from edifact.outgoing.models.name import Name


class TestMessageBirthAdaptor(unittest.TestCase):

    def test_create_message_segment_patient_details(self):
        with self.subTest("Patient with no previous names or addresses"):
            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            expected = MessageSegmentBirthPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                         date_of_birth="2019-04-20",
                                                         gender="1", address=edifact_pat_address)

            op_def = fixtures.create_operation_definition_for_birth_registration()

            msg_seg_pat_details = message_adaptor.create_message_segment_patient_detail(op_def)

            compare(msg_seg_pat_details, expected)

    def test_create_message_segment_registration_details(self):
        with self.subTest("Patient registration details for type birth"):
            expected = MessageSegmentBirthRegistrationDetails(transaction_number=17,
                                                              party_id="4826940,281",
                                                              acceptance_code="A",
                                                              acceptance_type=1,
                                                              date_time="2019-04-23 09:00:04.159338",
                                                              location="Spidey Town")

            op_def = fixtures.create_operation_definition_for_birth_registration()

            msg_seg_reg_details = message_adaptor.create_message_segment_registration_details(op_def)

            compare(msg_seg_reg_details, expected)
