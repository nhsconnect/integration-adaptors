from json import JSONDecodeError
from typing import Any

import tornado.web
from fhirclient.models.codeableconcept import CodeableConcept

from comms import proton_queue_adaptor
from tornado import httputil
from common.handler import base_handler
from outbound.schema.schema_validation_exception import SchemaValidationException

from utilities import integration_adaptors_logger as log, timing
from utilities import config, message_utilities

from fhirclient.models.operationoutcome import OperationOutcome, OperationOutcomeIssue

from outbound.schema import validate_request
import json

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.fhir_to_edifact import FhirToEdifact

logger = log.IntegrationAdaptorsLogger(__name__)


class AcceptanceAmendmentRequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
            host=config.get_config('OUTBOUND_QUEUE_HOST'),
            username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
            password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None))
        self.fhir_to_edifact = FhirToEdifact()
        self.mesh_wrapper = MeshOutboundWrapper(queue_adaptor)


    # def validate_uri_matches_payload_operation(self, operation, uri):
    #     string_length_of_operation = uri.find(operation)
    #     if (string_length_of_operation >= len(operation) - 1):
    #         return True
    #     else:
    #         return False

    def set_unsuccesful_response(self, status, code, coding_code, details):
        self.set_status(status)
        # TODO: Consider building this up programmatically instead?
        operation_outcome = OperationOutcome()
        outcome_issue = OperationOutcomeIssue()
        outcome_issue.severity = "error"
        outcome_issue.code = code
        issue_details = CodeableConcept()

        operationOutcomeIssue = OperationOutcomeIssue({
            "severity": "error",
            "code": code,
            "details": {
                "coding": [{
                    "system": "https://www.hl7.org/fhir/patient.html",
                    "version": "1",
                    "code": coding_code,
                    "display": details
                }]
            }
        })
        operationOutcome = OperationOutcome(operationOutcomeIssue.as_json())
        self.finish(operationOutcome)

    @timing.time_request
    async def post(self, patient_id):
        # TODO: Path should be POST /fhir/Patient/{id}. Need to check that {id} matches the identifier of the Patient in the payload
        try:
            # TODO: request with empty body causes unhandled error here
            request_body = json.loads(self.request.body.decode())
            # The JSONSchema for Patient requires a const resourceType = 'Patient' so this is not required
            # uri_matches_payload_operation = self.validate_uri_matches_payload_operation(
            #     request_body['resourceType'], self.request.uri)
            # if uri_matches_payload_operation:
            validate_request.validate_patient(request_body)
            edifact = self.fhir_to_edifact.convert(self.request.body.decode())
            unique_operation_id = message_utilities.get_uuid()
            await self.mesh_wrapper.send(edifact)
            self.set_status(202)
            self.set_header("OperationId", unique_operation_id)
            await self.finish()

            # else:
            #     self.set_unsuccesful_response(400, "value", "URI_DOES_NOT_MATCH_PAYLOAD_OPERATION",
            #                       f"Requested uri operation: {self.request.uri}, does not match payload operation requested: {request_body['resourceType']}.")
        except SchemaValidationException as e:
            details = f"'{e.path[0]}' {e.message}"
            self.set_unsuccesful_response(400, "value", "JSON_PAYLOAD_NOT_VALID_TO_SCHEMA", details)
        except JSONDecodeError:
            # TODO: create correct error response
            raise

    @timing.time_request
    async def patch(self, patient_id):
        self.set_status(202)
        await self.finish(f'Amendment for patient {patient_id}')
