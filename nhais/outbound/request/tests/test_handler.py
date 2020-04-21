import tornado.testing
from tornado.web import Application

from outbound.request import handler

import json
import os

root_dir = os.path.dirname(os.path.abspath(__file__))
json_patient = root_dir + "/data/patient.json"
with open(json_patient) as file:
    data = json.load(file)
REQUEST_BODY = json.dumps(data)
REQUEST_PATIENT_URI = "/fhir/Patient/abc"
REQUEST_VALID_OPERATION = "Patient"
REQUEST_INVALID_OPERATION = "Patientssss"


class TestHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return tornado.web.Application([(r'/fhir/Patient/.*', handler.Handler)])

    def test_invalid_post_request_line_return_404_response_code(self):

        response = self.fetch(r'/fhir/', method="POST",
                              body=REQUEST_BODY)

        self.assertEqual(404, response.code)

    # TODO: happy path

    # TODO: invalid payload triggers 400 error. Assert message and JSONPath to error in OperationOutcome response

    # def test_valid_operation_uri_and_payload_matches_true_response(self):
    #     response = handler.Handler.validate_uri_matches_payload_operation(self, REQUEST_VALID_OPERATION, REQUEST_PATIENT_URI)
    #
    #     self.assertEqual(True, response)
    #
    # def test_invalid_operation_uri_and_payload_matches_false_response(self):
    #     response = handler.Handler.validate_uri_matches_payload_operation(self, REQUEST_INVALID_OPERATION, REQUEST_PATIENT_URI)
    #
    #     self.assertEqual(False, response)
