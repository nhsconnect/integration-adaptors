import unittest

from fhirclient.models.patient import Patient
from testfixtures import compare

import adaptor.fhir_helpers.fhir_creators as creators
from adaptor.fhir_helpers.fhir_creators import ParameterName, ResourceType, OperationName
import adaptor.outgoing.death.message_death_adaptor as message_adaptor
import adaptor.outgoing.tests.fixtures as fixtures
from edifact.outgoing.models.death.message_death import MessageSegmentDeathPatientDetails, \
    MessageSegmentDeathRegistrationDetails
from edifact.outgoing.models.address import Address as EdifactAddress
from edifact.outgoing.models.name import Name


class TestMessageDeathAdaptor(unittest.TestCase):
    """
    Tests the conversion of fhir to edifact
    """

    def test_create_message_segment_patient_details(self):
        """
        Test the function to create an edifact segment for patient details
        """

        expected = MessageSegmentDeathPatientDetails(id_number="NHSNO11111")

        patient = fixtures.create_simple_patient()
        op_param_patient = creators.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PATIENT,
                                                                       resource_type=ResourceType.PATIENT,
                                                                       reference="patient-1")
        op_def = creators.create_operation_definition(name=OperationName.REGISTER_DEATH, code="gpc.registerpatient",
                                                      date_time="2019-04-23 09:00:04.159338", contained=[patient],
                                                      parameters=[op_param_patient])
        msg_seg_pat_details = message_adaptor.create_message_segment_patient_detail(op_def)

        compare(msg_seg_pat_details, expected)

    def test_create_message_segment_registration_details(self):
        """
        Test the function to create an edifact segment for the registration details
        """

        with self.subTest("Patient death registration details without free text"):
            expected = MessageSegmentDeathRegistrationDetails(transaction_number=17,
                                                              party_id="4826940,281",
                                                              date_time="2019-04-20 09:00:04.159338")

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
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_BIRTH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338",
                                                          contained=[practitioner, patient],
                                                          parameters=[op_param_transaction_number,
                                                                      op_param_practitioner, op_param_patient])

            msg_seg_reg_details = message_adaptor.create_message_segment_registration_details(op_def)

            compare(msg_seg_reg_details, expected)
