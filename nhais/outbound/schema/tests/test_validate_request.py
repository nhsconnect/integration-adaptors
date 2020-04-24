import unittest
import json
import os

from fhir.resources.fhirabstractbase import FHIRValidationError

from outbound.schema.schema_validation_exception import SchemaValidationException
from outbound.schema.validate_request import validate_patient

root_dir = os.path.dirname(os.path.abspath(__file__))

valid_json_patient = root_dir + "/../../../common/data/patient.json"
with open(valid_json_patient) as file:
    VALID_REQUEST_BODY = json.load(file)

invalid_json_patient_id = root_dir + "/../../../common/data/patient_invalid_id.json"
with open(invalid_json_patient_id) as file:
    INVALID_ID_REQUEST_BODY = json.load(file)

missing_json_patient_id = root_dir + "/../../../common/data/patient_missing_id.json"
with open(missing_json_patient_id) as file:
    MISSING_ID_REQUEST_BODY = json.load(file)

class TestValidateRequest(unittest.TestCase):

    def test_valid_schema(self):
        try:
            response = validate_patient(VALID_REQUEST_BODY)
        except SchemaValidationException:
            self.fail("myFunc() raised ExceptionType unexpectedly!")

        self.assertEqual('9000000009', response.id)
        self.assertEqual('Patient', response.resource_type)

    def test_missing_id(self):
        with self.assertRaises(SchemaValidationException) as e:
            validate_patient(MISSING_ID_REQUEST_BODY)

    def test_invalid_schema(self):
        with self.assertRaises(FHIRValidationError) as e:
            validate_patient(INVALID_ID_REQUEST_BODY)