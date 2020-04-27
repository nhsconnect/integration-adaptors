import json
import os
from unittest.mock import patch, MagicMock

import tornado.testing
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.operationoutcome import OperationOutcomeIssue, OperationOutcome
from tornado.web import Application

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.request.acceptance_amendment import AcceptanceAmendmentRequestHandler

root_dir = os.path.dirname(os.path.abspath(__file__))

REQUEST_PATIENT_URI = "/fhir/Patient/123"
REQUEST_VALID_OPERATION = "Patient"
REQUEST_INVALID_OPERATION = "Patientssss"

valid_json_patient = root_dir + "/../../../outbound/data/patient.json"
with open(valid_json_patient) as file:
    data = json.load(file)
VALID_REQUEST_BODY = json.dumps(data)

invalid_json_patient_id = root_dir + "/../../../outbound/data/patient_invalid_id.json"
with open(invalid_json_patient_id) as file:
    data = json.load(file)
INVALID_ID_REQUEST_BODY = json.dumps(data)

missing_json_patient_id = root_dir + "/../../../outbound/data/patient_missing_id.json"
with open(missing_json_patient_id) as file:
    data = json.load(file)
MISSING_ID_REQUEST_BODY = json.dumps(data)


class TestAcceptanceAmendmentRequestHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self) -> Application:
        return tornado.web.Application([(r'/fhir/Patient/(.*)', AcceptanceAmendmentRequestHandler)])

    async def async_magic(self):
        pass

    def create_operation_outcome(self, response_body):
        coding = Coding()
        coding.code = response_body['issue'][0]['details']['coding'][0]['code']
        coding.display = response_body['issue'][0]['details']['coding'][0]['display']
        coding.version = response_body['issue'][0]['details']['coding'][0]['version']
        coding.system = response_body['issue'][0]['details']['coding'][0]['version']

        details = CodeableConcept()
        details.coding = [coding]

        operation_outcome_issue = OperationOutcomeIssue()
        operation_outcome_issue.severity = response_body['issue'][0]['severity']
        operation_outcome_issue.code = response_body['issue'][0]['code']
        operation_outcome_issue.details = details

        operation_outcome = OperationOutcome()
        operation_outcome.issue = [operation_outcome_issue]

        return operation_outcome

    def test_invalid_post_request_line_return_404_response_code(self):
        response = self.fetch(r'/water/Panda/9000000009', method="POST",
                              body=VALID_REQUEST_BODY)
        self.assertEqual(404, response.code)
        self.assertEqual('Not Found', response.reason)

    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_happy_path(self, mock_init, mock_send):
        mock_init.return_value = None
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch(r'/fhir/Patient/9000000009', method="POST",
                              body=VALID_REQUEST_BODY)

        self.assertEqual(202, response.code)

    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_invalid_payload_id_not_string(self, mock_init, mock_send):
        mock_init.return_value = None
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/9000000009', method="POST",
                              body=INVALID_ID_REQUEST_BODY)

        operation_outcome = self.create_operation_outcome(json.loads(response.body.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('JSON_PAYLOAD_NOT_VALID_TO_SCHEMA', operation_outcome.issue[0].details.coding[0].code)
        self.assertEqual('OperationOutcome', operation_outcome.resource_type)
        self.assertEqual(400, response.code)

    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_patient_id_doesnt_match_uri_id(self, mock_init, mock_send):
        mock_init.return_value = None
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/2384763847264', method="POST",
                              body=VALID_REQUEST_BODY)

        operation_outcome = self.create_operation_outcome(json.loads(response.body.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('ID_IN_URI_DOES_NOT_MATCH_PAYLOAD_ID', operation_outcome.issue[0].details.coding[0].code)
        self.assertEqual('URI id `2384763847264` does not match PAYLOAD id `9000000009`', operation_outcome.issue[0].details.coding[0].display)
        self.assertEqual('OperationOutcome', operation_outcome.resource_type)
        self.assertEqual(400, response.code)

    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_patient_id_missing_id_in_payload(self, mock_init, mock_send):
        mock_init.return_value = None
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/90000009', method="POST",
                              body=MISSING_ID_REQUEST_BODY)

        operation_outcome = self.create_operation_outcome(json.loads(response.body.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('JSON_PAYLOAD_NOT_VALID_TO_SCHEMA', operation_outcome.issue[0].details.coding[0].code)
        self.assertEqual('id id is missing from payload.', operation_outcome.issue[0].details.coding[0].display)
        self.assertEqual('OperationOutcome', operation_outcome.resource_type)
        self.assertEqual(400, response.code)

    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_missing_payload(self, mock_init, mock_send):
        mock_init.return_value = None
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/90000009', method="POST", allow_nonstandard_methods=True)

        operation_outcome = self.create_operation_outcome(json.loads(response.body.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('PAYLOAD_IS_NOT_VALID_JSON_FORMAT', operation_outcome.issue[0].details.coding[0].code)
        self.assertEqual('Payload is either missing, empty or not valid to json, this is required.', operation_outcome.issue[0].details.coding[0].display)
        self.assertEqual('OperationOutcome', operation_outcome.resource_type)
        self.assertEqual(400, response.code)

