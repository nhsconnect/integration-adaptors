import tornado.testing
from tornado.web import Application

from outbound.request import acceptance_amendment

import json
import os

root_dir = os.path.dirname(os.path.abspath(__file__))

REQUEST_PATIENT_URI = "/fhir/Patient/123"
REQUEST_VALID_OPERATION = "Patient"
REQUEST_INVALID_OPERATION = "Patientssss"

valid_json_patient = root_dir + "/data/patient.json"
with open(valid_json_patient) as file:
    data = json.load(file)
VALID_REQUEST_BODY = json.dumps(data)

invalid_json_patient_id = root_dir + "/data/patient_invalid_id.json"
with open(invalid_json_patient_id) as file:
    data = json.load(file)
INVALID_ID_REQUEST_BODY = json.dumps(data)

MISSING_ID_REQUEST_BODY = json.dumps(None)


class TestAcceptanceAmendmentRequestHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self) -> Application:
        return tornado.web.Application([(r'/fhir/Patient/([0-9]*])', acceptance_amendment.AcceptanceAmendmentRequestHandler)])

    def test_invalid_post_request_line_return_404_response_code(self):
        response = self.fetch(r'/fhr/Patnt/9000000009', method="POST",
                              body=VALID_REQUEST_BODY)
        self.assertEqual(404, response.code)

    # TODO: happy path
    def test_happy_path(self):
        response = self.fetch('/fhir/Patient/9000000009', method="POST",
                              body=VALID_REQUEST_BODY)
        self.assertEqual(202, response.code)

    # TODO: invalid payload triggers 400 error. Assert message and JSONPath to error in OperationOutcome response
    def test_invalid_payload(self):
        response = self.fetch('http://localhost:80/fhir/Patient/9000000009', method="POST",
                              body=INVALID_ID_REQUEST_BODY)
        self.assertEqual(400, response.code)

    def test_patient_id_doesnt_match(self):
        response = self.fetch('http://localhost:80/fhir/Patient/90000009', method="POST",
                              body=VALID_REQUEST_BODY)
        self.assertEqual(400, response.code)

    def test_patient_id_doesnt_match(self):
        response = self.fetch('http://localhost:80/fhir/Patient/90000009', method="POST",
                              body=MISSING_ID_REQUEST_BODY)
        self.assertEqual(400, response.code)



    # def test_valid_operation_uri_and_payload_matches_true_response(self):
    #     response = handler.Handler.validate_uri_matches_payload_operation(self, REQUEST_VALID_OPERATION, REQUEST_PATIENT_URI)
    #
    #     self.assertEqual(True, response)
    #
    # def test_invalid_operation_uri_and_payload_matches_false_response(self):
    #     response = handler.Handler.validate_uri_matches_payload_operation(self, REQUEST_INVALID_OPERATION, REQUEST_PATIENT_URI)
    #
    #     self.assertEqual(False, response)
