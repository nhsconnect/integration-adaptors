import unittest

from testfixtures import compare

from adaptor.fhir_helpers import fhir_creators as creators
from adaptor.fhir_helpers.fhir_creators import ParameterName, ResourceType, OperationName
import adaptor.outgoing.message_adaptor as message_adaptor
import adaptor.outgoing.birth.tests.fixtures as fixtures
from edifact.outgoing.models.birth.message_birth import MessageSegmentBirthPatientDetails, \
    MessageSegmentBirthRegistrationDetails, MessageTypeBirth
from edifact.outgoing.models.address import Address as EdifactAddress
from edifact.outgoing.models.message import MessageBeginning
from edifact.outgoing.models.name import Name


class TestMessageAdaptor(unittest.TestCase):

    def test_create_message_beginning(self):
        with self.subTest("Message beginning for a birth registration"):
            expected = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")

            op_param_nhais_cypher = creators.create_parameter_with_binding(name=ParameterName.NHAIS_CYPHER, value="XX1")
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_BIRTH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338",
                                                          parameters=[op_param_nhais_cypher])

            msg_bgn = message_adaptor.create_message_beginning(fhir_operation=op_def)

            compare(msg_bgn, expected)

    def test_create_message(self):
        with self.subTest("Birth Registration"):
            msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")
            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            msg_seg_pat_details = MessageSegmentBirthPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                                    date_of_birth="2019-04-20",
                                                                    gender="1", address=edifact_pat_address)
            msg_seg_reg_details = MessageSegmentBirthRegistrationDetails(transaction_number=17,
                                                                         party_id="4826940,281",
                                                                         acceptance_code="A",
                                                                         acceptance_type=1,
                                                                         date_time="2019-04-23 09:00:04.159338",
                                                                         location="Spidey Town")
            expected = MessageTypeBirth(sequence_number="000001", message_beginning=msg_bgn,
                                        message_segment_registration_details=msg_seg_reg_details,
                                        message_segment_patient_details=msg_seg_pat_details)

            op_def = fixtures.create_operation_definition_for_birth_registration()

            message = message_adaptor.create_message(fhir_operation=op_def)

            compare(message, expected)

