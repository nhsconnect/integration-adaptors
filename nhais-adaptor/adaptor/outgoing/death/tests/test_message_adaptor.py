import unittest

from fhirclient.models.patient import Patient
from testfixtures import compare

from adaptor.fhir_helpers import fhir_creators as creators
from adaptor.fhir_helpers.fhir_creators import ParameterName, ResourceType, OperationName
import adaptor.outgoing.message_adaptor as message_adaptor
from adaptor.outgoing.tests import fixtures as fixtures
from edifact.outgoing.models.death.message_death import MessageSegmentDeathPatientDetails, \
    MessageSegmentDeathRegistrationDetails, MessageTypeDeath
from edifact.outgoing.models.message import MessageBeginning


class TestMessageAdaptor(unittest.TestCase):
    """
    Tests the conversion of fhir to edifact
    """

    def test_create_message_beginning(self):
        """
        Test the function to create an edifact section representing the beginning of a message
        """
        with self.subTest("Message beginning for a death registration"):
            expected = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G5")

            op_param_nhais_cypher = creators.create_parameter_with_binding(name=ParameterName.NHAIS_CYPHER, value="XX1")
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_DEATH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338", contained=[],
                                                          parameters=[op_param_nhais_cypher])

            msg_bgn = message_adaptor.create_message_beginning(fhir_operation=op_def)

            compare(msg_bgn, expected)

    def test_create_message(self):
        """
        Test the function to create an edifact message
        """
        with self.subTest("Birth Registration"):
            msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G5")
            msg_seg_pat_details = MessageSegmentDeathPatientDetails(id_number="NHSNO22222")
            msg_seg_reg_details = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                                         party_id="4826940,281",
                                                                         date_time="2019-04-20 09:00:04.159338")
            expected = MessageTypeDeath(sequence_number="000001", message_beginning=msg_bgn,
                                        message_segment_registration_details=msg_seg_reg_details,
                                        message_segment_patient_details=msg_seg_pat_details)

            op_param_message_sequence = creators.create_parameter_with_binding(name=ParameterName.MESSAGE_SEQ_NO,
                                                                               value="000001")
            op_param_nhais_cypher = creators.create_parameter_with_binding(name=ParameterName.NHAIS_CYPHER, value="XX1")
            op_param_transaction_number = creators.create_parameter_with_binding(name=ParameterName.TRANSACTION_NO,
                                                                                 value="17")
            practitioner = fixtures.create_simple_practitioner()
            patient = Patient({'id': 'patient-1',
                               'identifier': [{'value': 'NHSNO22222'}],
                               'deceasedBoolean': True,
                               'deceasedDateTime': '2019-04-20 09:00:04.159338'
                               })
            op_param_practitioner = creators.create_parameter_with_resource_ref(
                name=ParameterName.REGISTER_PRACTITIONER,
                resource_type=ResourceType.PRACTITIONER,
                reference="practitioner-1")
            op_param_patient = creators.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PATIENT,
                                                                           resource_type=ResourceType.PATIENT,
                                                                           reference="patient-1")
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_DEATH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338",
                                                          contained=[practitioner, patient],
                                                          parameters=[op_param_message_sequence,
                                                                      op_param_transaction_number,
                                                                      op_param_nhais_cypher,
                                                                      op_param_practitioner, op_param_patient])

            message = message_adaptor.create_message(fhir_operation=op_def)

            compare(message, expected)
