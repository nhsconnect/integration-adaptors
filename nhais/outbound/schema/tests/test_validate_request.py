import json
import os
import unittest
from unittest.mock import patch, PropertyMock

from fhir.resources.fhirabstractbase import FHIRValidationError
from fhir.resources.fhirelementfactory import FHIRElementFactory

from outbound.schema.request_validation_exception import RequestValidationException
from outbound.schema.validate_request import validate_patient

root_dir = os.path.dirname(os.path.abspath(__file__))

valid_json_patient = root_dir + "/../../../outbound/data/patient.json"
with open(valid_json_patient) as file:
    VALID_REQUEST_BODY = json.load(file)


class TestValidateRequest(unittest.TestCase):

    def test_valid_schema(self):
        response = validate_patient(VALID_REQUEST_BODY)

        patient = FHIRElementFactory.instantiate('Patient', response.as_json())

        self.assertEqual('9000000009', patient.id)
        self.assertEqual('Patient', patient.resource_type)

    @patch.object(FHIRElementFactory, "instantiate")
    def test_missing_id(self, mock):


        with self.assertRaises(RequestValidationException) as ex:
            validate_patient({'test': 'test'})

        # TODO: Does the exception have the message and path that is expected? It is likely that the error or errors
        #  are not actually related to id since the payload is not a Patient at all. Use the patient_missing_id.json
        #  here instead
        ex.exception

    @patch("outbound.schema.validate_request._parse_fhir_errors")
    @patch('fhir.resources.fhirelementfactory.FHIRElementFactory.instantiate',
           side_effect=FHIRValidationError('error'))
    def test_invalid_id(self, mock, mock2):
        # TODO: Its not clear what this is testing and protected members should not be mocked. Remove?
        type(mock2).return_value = PropertyMock(return_value=[('id', 'error message')])
        with self.assertRaises(RequestValidationException):
            validate_patient({"test": "test"})

    # TODO: test validation of a payload containing multiple validation errors