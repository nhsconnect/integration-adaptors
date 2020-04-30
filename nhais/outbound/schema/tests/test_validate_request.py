import json
import os
import unittest
from unittest.mock import patch

from fhir.resources.fhirelementfactory import FHIRElementFactory

from outbound.schema.request_validation_exception import RequestValidationException
from outbound.schema.validate_request import validate_patient

root_dir = os.path.dirname(os.path.abspath(__file__))

valid_json_patient = root_dir + "/data/patient.json"
with open(valid_json_patient) as file:
    VALID_REQUEST_BODY = json.load(file)

invalid_json_patient_id = root_dir + "/data/patient_invalid_id.json"
with open(invalid_json_patient_id) as file:
    INVALID_ID_REQUEST_BODY = json.load(file)

missing_json_patient_id = root_dir + "/data/patient_missing_id.json"
with open(missing_json_patient_id) as file:
    MISSING_ID_REQUEST_BODY = json.load(file)

multiple_invalid_patient_payload = root_dir + "/data/patient_payload_multiple_invalid.json"
with open(multiple_invalid_patient_payload) as file:
    MULTIPLE_INVALID_REQUEST_BODY = json.load(file)


class TestValidateRequest(unittest.TestCase):

    def test_valid_patient_payload(self):
        response = validate_patient(VALID_REQUEST_BODY)

        patient = FHIRElementFactory.instantiate('Patient', response.as_json())

        self.assertEqual('9000000009', patient.id)
        self.assertEqual('Patient', patient.resource_type)

    @patch.object(FHIRElementFactory, "instantiate")
    def test_missing_id_from_payload(self, mock):
        with self.assertRaises(RequestValidationException) as e:
            validate_patient(MISSING_ID_REQUEST_BODY)

        self.assertEqual('id', e.exception.errors[0].path)
        self.assertEqual('id is missing from payload.', e.exception.errors[0].message)

    def test_invalid_variable_int_for_id_string(self):
        with self.assertRaises(RequestValidationException) as e:
            validate_patient(INVALID_ID_REQUEST_BODY)

        self.assertEqual('id', e.exception.errors[0].path)
        self.assertEqual('Wrong type <class \'int\'> for property "id" on <class \'fhir.resources.patient.Patient\'>, expecting <class \'str\'>', e.exception.errors[0].message)

    def test_invalid_payload_containing_multiple_validation_errors(self):
        with self.assertRaises(RequestValidationException) as e:
            validate_patient(MULTIPLE_INVALID_REQUEST_BODY)

        self.assertEqual('id', e.exception.errors[0].path)
        self.assertEqual('Wrong type <class \'int\'> for property "id" on <class \'fhir.resources.patient.Patient\'>, expecting <class \'str\'>', e.exception.errors[0].message)
        self.assertEqual('meta.versionId', e.exception.errors[1].path)
        self.assertEqual('Wrong type <class \'int\'> for property "versionId" on <class \'fhir.resources.meta.Meta\'>, expecting <class \'str\'>', e.exception.errors[1].message)