import unittest
import json
import adaptor.incoming.operation_definition_adaptor as adaptor
import edifact.incoming.parser.deserialiser as deserialiser
from testfixtures import compare


class TestEdifactToFhirIntegration(unittest.TestCase):
    """
    Test that when fhir json payload is loaded the correct edifact message is created
    """

    def test_patient_registration_birth_approval(self):
        """
        Test when the operation is for a birth registration
        """
        with open("./tests/incoming/edifact.txt", "r") as incoming_edifact_file:
            incoming_interchange_raw = incoming_edifact_file.read()

        with open("./tests/incoming/patient-register-birth-approval.json", "r") as patient_register_approval:
            patient_register_approval_json = json.load(patient_register_approval)

        lines = incoming_interchange_raw.split("'\n")
        interchange = deserialiser.convert(lines)

        op_defs = adaptor.create_operation_definition(interchange)
        pretty_op_def = op_defs[0][1].as_json()

        compare(pretty_op_def, patient_register_approval_json)
