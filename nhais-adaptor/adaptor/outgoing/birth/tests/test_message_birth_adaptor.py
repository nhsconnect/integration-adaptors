import unittest

from testfixtures import compare

import adaptor.fhir_helpers.fhir_creators as creators
from adaptor.fhir_helpers.fhir_creators import ParameterName, ResourceType, OperationName
import adaptor.outgoing.birth.message_birth_adaptor as message_adaptor
import adaptor.outgoing.tests.fixtures as fixtures
from edifact.outgoing.models.Birth.message_birth import MessageSegmentBirthPatientDetails, \
    MessageSegmentBirthRegistrationDetails
from edifact.outgoing.models.address import Address as EdifactAddress
from edifact.outgoing.models.name import Name


class TestMessageAdaptor(unittest.TestCase):
    """
    Tests the conversion of fhir to edifact
    """

    def test_create_message_segment_patient_details(self):
        """
        Test the function to create an edifact segment for patient details
        """

        with self.subTest("Patient with no previous names or addresses"):
            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            expected = MessageSegmentBirthPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                         date_of_birth="2019-04-20",
                                                         gender="1", address=edifact_pat_address)

            patient = fixtures.create_simple_patient()
            op_param_patient = creators.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PATIENT,
                                                                           resource_type=ResourceType.PATIENT,
                                                                           reference="patient-1")
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_BIRTH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338", contained=[patient],
                                                          parameters=[op_param_patient])
            msg_seg_pat_details = message_adaptor.create_message_segment_patient_detail(op_def)

            compare(msg_seg_pat_details, expected)

    def test_create_message_segment_registration_details(self):
        """
        Test the function to create an edifact segment for the registration details
        """

        with self.subTest("Patient registration details for type birth"):
            expected = MessageSegmentBirthRegistrationDetails(transaction_number=17,
                                                              party_id="4826940,281",
                                                              acceptance_code="A",
                                                              acceptance_type=1,
                                                              date_time="2019-04-23 09:00:04.159338",
                                                              location="Spidey Town")

            op_param_transaction_number = creators.create_parameter_with_binding(name=ParameterName.TRANSACTION_NO,
                                                                                 value="17")
            practitioner = fixtures.create_simple_practitioner()
            patient = fixtures.create_simple_patient()
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

