import unittest

from fhirclient.models.patient import Patient
from fhirclient.models.operationdefinition import OperationDefinitionParameter, OperationDefinition
from fhirclient.models.practitioner import Practitioner

import adaptor.outgoing.fhir_helpers.fhir_creators as creators
from adaptor.outgoing.fhir_helpers.fhir_creators import ResourceType


class TestFhirCreators(unittest.TestCase):
    """
    Tests the helper functions for the fhir operation definition
    """

    def test_create_parameter_with_binding(self):
        """
        Test the helper function to create an operation parameter with a binding value
        """
        op_param = creators.create_parameter_with_binding(name="SOME_NAME", value="SOME_VALUE")

        self.assertIsInstance(op_param, OperationDefinitionParameter)
        self.assertEqual(op_param.name, "SOME_NAME")
        self.assertEqual(op_param.binding.valueSetReference.identifier.value, "SOME_VALUE")

    def test_create_parameter_with_resource_ref(self):
        """
        Test the helper function to create an operation parameter with a resource reference
        """
        op_param = creators.create_parameter_with_resource_ref(name="SOME_NAME",
                                                               resource_type=ResourceType.PRACTITIONER,
                                                               reference="practitioner-1")

        self.assertIsInstance(op_param, OperationDefinitionParameter)
        self.assertEqual(op_param.name, "SOME_NAME")
        self.assertEqual(op_param.type, ResourceType.PRACTITIONER)
        self.assertEqual(op_param.profile.reference, "#practitioner-1")

    def test_create_operation_definition(self):
        """
        Tests the helper function to create an operation definition
        """

        with self.subTest("with no contained resources or parameters"):
            op_def = creators.create_operation_definition(name="name.of.operation", code="code.of.operation",
                                                          date_time="2019-04-23 09:00:04.159338", contained=[],
                                                          parameters=[])

            self.assertIsInstance(op_def, OperationDefinition)
            self.assertEqual(op_def.name, "name.of.operation")
            self.assertEqual(op_def.code, "code.of.operation")
            self.assertEqual(op_def.date.as_json(), "2019-04-23 09:00:04.159338")
            self.assertEqual(op_def.contained, None)
            self.assertEqual(op_def.parameter, None)

        with self.subTest("with one parameter"):
            some_param = creators.create_parameter_with_binding(name="SOME_NAME", value="SOME_VALUE")

            op_def = creators.create_operation_definition(name="name.of.operation", code="code.of.operation",
                                                          date_time="2019-04-23 09:00:04.159338", contained=[],
                                                          parameters=[some_param])

            self.assertEqual(len(op_def.parameter), 1)
            self.assertIsInstance(op_def.parameter[0], OperationDefinitionParameter)

        with self.subTest("with one contained resource"):
            some_resource = creators.create_practitioner_resource(resource_id="some_id",
                                                                  national_identifier="some_nat_id",
                                                                  local_identifier="some_local_id")

            op_def = creators.create_operation_definition(name="name.of.operation", code="code.of.operation",
                                                          date_time="2019-04-23 09:00:04.159338",
                                                          contained=[some_resource],
                                                          parameters=[])

            self.assertEqual(len(op_def.contained), 1)
            self.assertIsInstance(op_def.contained[0], Practitioner)

    def test_create_practitioner(self):
        practitioner = creators.create_practitioner_resource(resource_id="practitioner-1",
                                                             national_identifier="1234567",
                                                             local_identifier="111")

        self.assertIsInstance(practitioner, Practitioner)
        self.assertEqual(practitioner.id, "practitioner-1")
        self.assertEqual(practitioner.identifier[0].value, "1234567")
        self.assertEqual(practitioner.identifier[1].value, "111")

    def test_create_patient(self):
        patient = creators.create_patient_resource(resource_id="patient-1", nhs_number="NHSNO11111",
                                                   title="Mr", first_name="Peter", last_name="Parker",
                                                   gender="male", date_of_birth="2019-04-23",
                                                   place_of_birth="Spidey Town",
                                                   address_line_1="1 Spidey Way", city="Spidey Town",
                                                   postcode="SP1 1AA")

        self.assertIsInstance(patient, Patient)
        self.assertEqual(patient.id, "patient-1")
        self.assertEqual(patient.identifier[0].value, "NHSNO11111")
        self.assertEqual(patient.name[0].prefix[0], "Mr")
        self.assertEqual(patient.name[0].given[0], "Peter")
        self.assertEqual(patient.name[0].family, "Parker")
        self.assertEqual(patient.gender, "male")
        self.assertEqual(patient.birthDate.as_json(), "2019-04-23")
        self.assertEqual(patient.extension[0].valueAddress.city, "Spidey Town")
        self.assertEqual(patient.address[0].line[0], "1 Spidey Way")
        self.assertEqual(patient.address[0].city, "Spidey Town")
        self.assertEqual(patient.address[0].postalCode, "SP1 1AA")
