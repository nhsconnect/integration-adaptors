import unittest
import json
from fhirclient.models.operationdefinition import OperationDefinition
from adaptor.outgoing.interchange_adaptor import InterchangeAdaptor


class FhirToEdifactIntegrationTest(unittest.TestCase):
    """
    Test that when fhir json payload is loaded the correct edifact message is created
    """

    def test_patient_registration_birth(self):
        """
        Test when the operation is for a birth registration
        """
        with open("./tests/edifact.txt", "r") as expected_file:
            expected_edifact_interchange = expected_file.read()

        with open("./tests/patient-register-birth.json", "r") as patient_register:
            patient_register_json = json.load(patient_register)
        op_def = OperationDefinition(patient_register_json)
        edifact_interchange = InterchangeAdaptor.create_interchange(fhir_operation=op_def)
        generated_edifact_interchange = "'\n".join(edifact_interchange.split("'"))

        self.assertEqual(generated_edifact_interchange, expected_edifact_interchange)

