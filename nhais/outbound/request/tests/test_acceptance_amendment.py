import json
import os
from unittest.mock import patch, MagicMock

import tornado.testing
from fhir.resources.fhirelementfactory import FHIRElementFactory
from fhir.resources.operationoutcome import OperationOutcomeIssue
from fhir.resources.patient import Patient
from tornado.web import Application

from edifact.edifact_exception import EdifactValidationException
from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.interchange_translator import InterchangeTranslator
from outbound.request.acceptance_amendment import AcceptanceAmendmentRequestHandler
from outbound.schema import validate_request
from outbound.schema.request_validation_exception import RequestValidationException, ValidationError
from utilities import message_utilities
from utilities.test_utilities import awaitable, awaitable_exception

root_dir = os.path.dirname(os.path.abspath(__file__))

REQUEST_PATIENT_URI = "/fhir/Patient/123"
REQUEST_VALID_OPERATION = "Patient"
REQUEST_INVALID_OPERATION = "Patientssss"

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"


class TestAcceptanceAmendmentRequestHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self) -> Application:
        return tornado.web.Application([(r'/fhir/Patient/(.*)', AcceptanceAmendmentRequestHandler)])

    def create_request_body(self, id='9000000009'):
        return json.dumps(self.create_patient(id).as_json())

    def create_patient(self, id='9000000009') -> Patient:
        p = Patient()
        p.id = id
        return p

    async def async_magic(self):
        pass

    def test_invalid_post_request_line_return_404_response_code(self):
        response = self.fetch(r'/water/Panda/9000000009', method="POST", body=self.create_request_body())
        self.assertEqual(404, response.code)
        self.assertEqual('Not Found', response.reason)

    @patch.object(InterchangeTranslator, 'convert')
    @patch.object(validate_request, 'validate_patient')
    @patch.object(message_utilities, "get_uuid")
    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_happy_path(self, mock_init, mock_send, mock_get_uuid, mock_validate_patient, mock_convert):
        mock_init.return_value = None
        mock_get_uuid.return_value = MOCK_UUID
        mock_validate_patient.return_value = self.create_patient()
        mock_convert.return_value = awaitable('EDIFACT')
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch(r'/fhir/Patient/9000000009', method="POST", body=self.create_request_body())

        self.assertEqual(202, response.code)
        self.assertEqual(MOCK_UUID, response.headers._dict['Operationid'])

    @patch.object(validate_request, 'validate_patient')
    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_patient_id_doesnt_match_uri_id(self, mock_init, mock_send, mock_validate_patient):
        mock_init.return_value = None
        mock_validate_patient.return_value = self.create_patient()
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/2384763847264', method="POST", body=self.create_request_body())

        operation_outcome = FHIRElementFactory.instantiate('OperationOutcome', json.loads(response.body.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('id', operation_outcome.issue[0].expression[0])
        self.assertEqual('Identifier in URI does not match identifier in request body', operation_outcome.issue[0].details.text)
        self.assertEqual(400, response.code)

    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_missing_payload(self, mock_init, mock_send):
        mock_init.return_value = None
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/90000009', method="POST", body='')

        operation_outcome = FHIRElementFactory.instantiate('OperationOutcome', json.loads(response.body.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('', operation_outcome.issue[0].expression[0])
        self.assertEqual('Request body is not parsable as JSON', operation_outcome.issue[0].details.text)
        self.assertEqual(400, response.code)

    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_payload_invalid_json(self, mock_init, mock_send):
        mock_init.return_value = None
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/90000009', method="POST", body='{ "json_fragment"')

        operation_outcome = FHIRElementFactory.instantiate('OperationOutcome', json.loads(response.body.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('', operation_outcome.issue[0].expression[0])
        self.assertEqual('Request body is not parsable as JSON', operation_outcome.issue[0].details.text)
        self.assertEqual(400, response.code)

    @patch('outbound.schema.validate_request.validate_patient',
           side_effect=RequestValidationException([ValidationError(path='path1', message='message1'),
                                                   ValidationError(path='path2', message='message2')]))
    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_two_errors_in_fhir_schema(self, mock_init, mock_send, mock_validate_patient):
        mock_init.return_value = None

        mock_validate_patient.return_value = self.create_patient()
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/9000000009', method="POST", body=self.create_request_body())

        operation_outcome = FHIRElementFactory.instantiate('OperationOutcome', json.loads(response.body.decode()))

        self.assertEqual('validationfail', operation_outcome.id)
        self.assertEqual(2, len(operation_outcome.issue))
        first = operation_outcome.issue[0]  # type: OperationOutcomeIssue
        self.assertEqual('error', first.severity)
        self.assertEqual('structure', first.code)
        self.assertEqual('path1', first.expression[0])
        self.assertEqual('message1', first.details.text)
        second = operation_outcome.issue[1]  # type: OperationOutcomeIssue
        self.assertEqual('error', second.severity)
        self.assertEqual('structure', second.code)
        self.assertEqual('path2', second.expression[0])
        self.assertEqual('message2', second.details.text)
        self.assertEqual(400, response.code)


    @patch.object(InterchangeTranslator, 'convert')
    @patch.object(validate_request, 'validate_patient')
    @patch.object(MeshOutboundWrapper, "send")
    @patch.object(MeshOutboundWrapper, "__init__")
    def test_edifact_translation_error(self, mock_init, mock_send, mock_validate_patient, mock_convert):
        mock_init.return_value = None
        mock_validate_patient.return_value = self.create_patient()
        mock_convert.return_value = awaitable_exception(EdifactValidationException('error message'))
        MagicMock.__await__ = lambda x: self.async_magic().__await__()

        response = self.fetch('/fhir/Patient/9000000009', method="POST", body=self.create_request_body())

        operation_outcome = FHIRElementFactory.instantiate('OperationOutcome', json.loads(response.body.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('', operation_outcome.issue[0].expression[0])
        self.assertEqual('error message', operation_outcome.issue[0].details.text)
        self.assertEqual(400, response.code)
