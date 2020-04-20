from typing import Any

from comms import proton_queue_adaptor
from tornado import httputil
from common.handler import base_handler

from utilities import integration_adaptors_logger as log, timing
from utilities import config, message_utilities

import generate_jsonschema
import json
import os

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.fhir_to_edifact import FhirToEdifact

logger = log.IntegrationAdaptorsLogger(__name__)


class Handler(base_handler.BaseHandler):

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
            host=config.get_config('OUTBOUND_QUEUE_HOST'),
            username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
            password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None))
        self.fhir_to_edifact = FhirToEdifact()
        self.mesh_wrapper = MeshOutboundWrapper(queue_adaptor)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_schema_patient = root_dir + "/json-schema-patient.json"

    def validate_uri_matches_payload_operation(self, operation, uri):
        string_length_of_operation = uri.find(operation)
        if (string_length_of_operation >= len(operation) - 1):
            return True
        else:
            return False

    def set_unsuccesful_response(self, status, code, coding_code, details):
        self.set_status(status)
        data = {"issue":
            [{
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
            }]
        }
        payload = {'resourceType': 'OperationOutcome', 'OperationOutcome': data}
        self.finish(payload)

    @timing.time_request
    async def post(self):
        request_body = json.loads(self.request.body.decode())
        uri_matches_payload_operation = self.validate_uri_matches_payload_operation(
            request_body['resourceType'], self.request.uri)
        if uri_matches_payload_operation:
            exception_thrown = generate_jsonschema.validate_schema(request_body, self.json_schema_patient)
            if exception_thrown is None:
                edifact = self.fhir_to_edifact.convert(self.request.body.decode())
                unique_operation_id = message_utilities.get_uuid()
                await self.mesh_wrapper.send(edifact)
                self.set_header("OperationId", unique_operation_id)
                await self.finish()
            else:
                details = f"'{exception_thrown.path[0]}' {exception_thrown.message}"
                self.set_unsuccesful_response(400, "value", "JSON_PAYLOAD_NOT_VALID_TO_SCHEMA",
                                  details)
        else:
            self.set_unsuccesful_response(400, "value", "URI_DOES_NOT_MATCH_PAYLOAD_OPERATION",
                              f"Requested uri operation: {self.request.uri}, does not match payload operation requested: {request_body['resourceType']}.")
