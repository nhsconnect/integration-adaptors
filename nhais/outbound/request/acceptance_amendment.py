from json import JSONDecodeError
from typing import Any

import tornado.web


from tornado import httputil
from outbound.schema.schema_validation_exception import SchemaValidationException

from utilities import integration_adaptors_logger as log, timing
from utilities import message_utilities

from outbound.schema import validate_request
import json

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.fhir_to_edifact import FhirToEdifact

logger = log.IntegrationAdaptorsLogger(__name__)


class AcceptanceAmendmentRequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self.fhir_to_edifact = FhirToEdifact()
        self.mesh_wrapper = MeshOutboundWrapper()

    def set_unsuccesful_response(self, status, code, coding_code, details):
        self.set_status(status)
        # TODO: Consider building this up programmatically instead? Block until reliable library is found
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
    async def post(self, patient_id):

        try:
            request_body = json.loads(self.request.body.decode())
            if "id" in request_body:
                if(request_body['id'] == patient_id):
                    validate_request.validate_patient(request_body)
                    edifact = self.fhir_to_edifact.convert(self.request.body.decode())
                    unique_operation_id = message_utilities.get_uuid()
                    await self.mesh_wrapper.send(edifact)
                    self.set_status(202)
                    self.set_header("OperationId", unique_operation_id)
                    await self.finish()
                else:
                    self.set_unsuccesful_response(400, "value", "ID_MISMATCH_URI_AND_PAYLOAD",f"URI id `{patient_id}` does not match PAYLOAD id `{request_body['id']}`")
            else:
                self.set_unsuccesful_response(400, "value", "JSON_PAYLOAD_MISSING_ID", "Could not find 'id' in payload")
        except SchemaValidationException as e:
            if hasattr(e, 'message'):
                details = f"{e.message}"
                self.set_unsuccesful_response(400, "value", "JSON_PAYLOAD_NOT_VALID_TO_SCHEMA", details)
        except JSONDecodeError:
                self.set_unsuccesful_response(400, "value", "JSON_PAYLOAD_IS_MISSING", "Payload is missing, Payload required.")


    @timing.time_request
    async def patch(self, patient_id):
        self.set_status(202)
        await self.finish(f'Amendment for patient `{patient_id}')
