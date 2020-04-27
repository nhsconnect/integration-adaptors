import json
import os
import unittest

from fhir.resources.fhirelementfactory import FHIRElementFactory

from outbound.schema.request_validation_exception import RequestValidationException
from outbound.schema.validate_request import validate_patient

root_dir = os.path.dirname(os.path.abspath(__file__))

valid_json_patient = root_dir + "/../../../outbound/data/patient.json"
with open(valid_json_patient) as file:
    VALID_REQUEST_BODY = json.load(file)

invalid_json_patient_id = root_dir + "/../../../outbound/data/patient_invalid_id.json"
with open(invalid_json_patient_id) as file:
    INVALID_ID_REQUEST_BODY = json.load(file)

missing_json_patient_id = root_dir + "/../../../outbound/data/patient_missing_id.json"
with open(missing_json_patient_id) as file:
    MISSING_ID_REQUEST_BODY = json.load(file)


class TestValidateRequest(unittest.TestCase):

    def test_valid_schema(self):
        response = validate_patient(VALID_REQUEST_BODY)

        patient = FHIRElementFactory.instantiate('Patient', response.as_json())

        self.assertEqual('9000000009', patient.id)
        self.assertEqual('Patient', patient.resource_type)

    def test_missing_id(self):
        with self.assertRaises(RequestValidationException) as e:
            validate_patient(MISSING_ID_REQUEST_BODY)

    def test_invalid_schema(self):
        with self.assertRaises(RequestValidationException) as e:
            validate_patient(INVALID_ID_REQUEST_BODY)
