import unittest

from testfixtures import compare

import adaptor.fhir_helpers.fhir_creators as creators
import adaptor.fhir_helpers.fhir_finders as finders
from adaptor.fhir_helpers.fhir_creators import ParameterName, ResourceType


class TestFhirFinders(unittest.TestCase):
    """
    Test the helper function to find particular values from a fhir operation definition
    """

    def test_get_parameter_value(self):
        op_param_transaction_number = creators.create_parameter_with_binding(name="some_param_name", value="17")

        op = creators.create_operation_definition(name="some.name", code="some.code",
                                                  date_time="2019-04-23 09:00:04.159338",
                                                  parameters=[op_param_transaction_number], contained=[])

        self.assertEqual(finders.get_parameter_value(op, "some_param_name"), "17")

    def test_find_resource(self):
        with self.subTest("When practitioner details are found in the operation definition"):
            practitioner = creators.create_practitioner_resource(resource_id="practitioner-1",
                                                                 national_identifier="1234567",
                                                                 local_identifier="111")
            op_param_practitioner = creators.create_parameter_with_resource_ref(
                name=ParameterName.REGISTER_PRACTITIONER,
                resource_type=ResourceType.PRACTITIONER,
                reference="practitioner-1")
            op_def = creators.create_operation_definition(name="name.of.operation", code="code.of.operation",
                                                          date_time="2019-04-23 09:00:04.159338",
                                                          parameters=[op_param_practitioner], contained=[practitioner])

            found_practitioner = finders.find_resource(fhir_operation=op_def, resource_type=ResourceType.PRACTITIONER)

            compare(found_practitioner, practitioner)
