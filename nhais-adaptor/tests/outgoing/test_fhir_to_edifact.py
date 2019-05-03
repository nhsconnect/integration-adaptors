import unittest
import json
from fhirclient.models.operationdefinition import OperationDefinition
import adaptor.outgoing.interchange_adaptor as adaptor


class TestFhirToEdifactIntegration(unittest.TestCase):
    """
    Test that when fhir json payload is loaded the correct edifact message is created
    """

    def test_patient_registration_birth(self):
        """
        Test when the operation is for a birth registration
        """
        with open("./tests/outgoing/edifact.txt", "r") as expected_file:
            expected_edifact_interchange = expected_file.read()

        with open("./tests/outgoing/patient-register-birth.json", "r") as patient_register:
            patient_register_json = json.load(patient_register)
        op_def = OperationDefinition(patient_register_json)
        edifact_interchange = adaptor.create_interchange(fhir_operation=op_def)
        pretty_edifact_interchange = "'\n".join(edifact_interchange.split("'"))

        self.assertEqual(pretty_edifact_interchange, expected_edifact_interchange)
