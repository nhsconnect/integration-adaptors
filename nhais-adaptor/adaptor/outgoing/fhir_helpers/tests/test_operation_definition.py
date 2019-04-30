import unittest

from fhirclient.models.patient import Patient
from testfixtures import compare
from fhirclient.models.operationdefinition import OperationDefinitionParameter, OperationDefinition
from fhirclient.models.practitioner import Practitioner

from adaptor.outgoing.fhir_helpers.operation_definition import OperationDefinitionHelper as odh
from adaptor.outgoing.fhir_helpers.constants import ParameterName, ResourceType


class OperationDefinitionHelperTest(unittest.TestCase):
    """
    Tests the helper functions for the fhir operation definition
    """

    def test_create_parameter_with_binding(self):
        """
        Test the helper function to create an operation parameter with a binding value
        """
        op_param = odh.create_parameter_with_binding(name="SOME_NAME", value="SOME_VALUE")

        self.assertIsInstance(op_param, OperationDefinitionParameter)
        self.assertEqual(op_param.name, "SOME_NAME")
        self.assertEqual(op_param.binding.valueSetReference.identifier.value, "SOME_VALUE")

    def test_create_parameter_with_resource_ref(self):
        """
        Test the helper function to create an operation parameter with a resource reference
        """
        op_param = odh.create_parameter_with_resource_ref(name="SOME_NAME", resource_type=ResourceType.PRACTITIONER,
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
            op_def = odh.create_operation_definition(name="name.of.operation", code="code.of.operation",
                                                     date_time="2019-04-23 09:00:04.159338", contained=[],
                                                     parameters=[])

            self.assertIsInstance(op_def, OperationDefinition)
            self.assertEqual(op_def.name, "name.of.operation")
            self.assertEqual(op_def.code, "code.of.operation")
            self.assertEqual(op_def.date.as_json(), "2019-04-23 09:00:04.159338")
            self.assertEqual(op_def.contained, None)
            self.assertEqual(op_def.parameter, None)

        with self.subTest("with one parameter"):
            some_param = odh.create_parameter_with_binding(name="SOME_NAME", value="SOME_VALUE")

            op_def = odh.create_operation_definition(name="name.of.operation", code="code.of.operation",
                                                     date_time="2019-04-23 09:00:04.159338", contained=[],
                                                     parameters=[some_param])

            self.assertEqual(len(op_def.parameter), 1)
            self.assertIsInstance(op_def.parameter[0], OperationDefinitionParameter)

    def test_create_practitioner(self):
        practitioner = odh.create_practitioner_resource(resource_id="practitioner-1", national_identifier="1234567",
                                                        local_identifier="111")

        self.assertIsInstance(practitioner, Practitioner)
        self.assertEqual(practitioner.id, "practitioner-1")
        self.assertEqual(practitioner.identifier[0].value, "1234567")
        self.assertEqual(practitioner.identifier[1].value, "111")

    def test_create_patient(self):
        patient = odh.create_patient_resource(resource_id="patient-1", nhs_number="NHSNO11111",
                                              title="Mr", first_name="Peter", last_name="Parker",
                                              gender="male", date_of_birth="2019-04-23", place_of_birth="Spidey Town",
                                              address_line_1="1 Spidey Way", city="Spidey Town", postcode="SP1 1AA")

        self.assertIsInstance(patient, Patient)

    def test_get_parameter_value(self):
        op_param_transaction_number = odh.create_parameter_with_binding(name="some_param_name", value="17")

        op = odh.create_operation_definition(name="some.name", code="some.code", date_time="2019-04-23 09:00:04.159338",
                                             contained=[], parameters=[op_param_transaction_number])

        self.assertEqual(odh.get_parameter_value(op, "some_param_name"), "17")

    def test_find_resource(self):
        with self.subTest("When practitioner details are found in the operation definition"):
            practitioner = odh.create_practitioner_resource(resource_id="practitioner-1", national_identifier="1234567",
                                                            local_identifier="111")
            op_param_practitioner = odh.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PRACTITIONER,
                                                                           resource_type=ResourceType.PRACTITIONER,
                                                                           reference="practitioner-1")
            op_def = odh.create_operation_definition(name="name.of.operation", code="code.of.operation",
                                                     date_time="2019-04-23 09:00:04.159338", contained=[practitioner],
                                                     parameters=[op_param_practitioner])

            found_practitioner = odh.find_resource(fhir_operation=op_def, resource_type=ResourceType.PRACTITIONER)

            compare(found_practitioner, practitioner)
