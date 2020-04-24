from json import JSONDecodeError
from typing import Any

import tornado.web
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.fhirabstractbase import FHIRValidationError
from fhir.resources.operationoutcome import OperationOutcome
from fhir.resources.operationoutcome import OperationOutcomeIssue

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

    def __set_unsuccesful_response(self, status, code, coding_code, details):
        self.set_status(status)
        # TODO: Consider building this up programmatically instead? Block until reliable library is found
        self.set_status(status)

        coding = Coding()
        coding.code = coding_code
        coding.display = details
        coding.version = '1'
        coding.system = 'https://www.hl7.org/fhir/patient.html'

        details = CodeableConcept()
        details.coding = [coding]

        pat2 = OperationOutcomeIssue()
        pat2.severity = 'error'
        pat2.code = code
        pat2.details = details

        pat = OperationOutcome()
        pat.issue = [pat2]

        data = {
            "issue":
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

        self.finish(pat.as_json())

    @timing.time_request
    async def post(self, patient_id):
        try:
            request_body = json.loads(self.request.body.decode())
            patient = validate_request.validate_patient(request_body)
            if (request_body['id'] == patient_id):
                edifact = self.fhir_to_edifact.convert(patient)
                unique_operation_id = message_utilities.get_uuid()
                await self.mesh_wrapper.send(edifact)
                self.set_status(202)
                self.set_header("OperationId", unique_operation_id)
                await self.finish()
            else:
                self.__set_unsuccesful_response(400, "value", "ID_IN_URI_DOES_NOT_MATCH_PAYLOAD_ID",
                                              f"URI id `{patient_id}` does not match PAYLOAD id `{request_body['id']}`")
        except SchemaValidationException as e:
            if hasattr(e, 'message'):
                details = f"{e.message}"
                self.__set_unsuccesful_response(400, "value", "JSON_PAYLOAD_NOT_VALID_TO_SCHEMA", details)
        except JSONDecodeError as e:
            self.__set_unsuccesful_response(400, "value", "PAYLOAD_IS_NOT_JSON_FORMAT",
                                          "Payload is missing, Payload required.")
        except TypeError as e:
            self.__set_unsuccesful_response(400, "value", "ID_IN_PAYLOAD_IS_MISSING",
                                            'Payload is missing id, id is required.')
        except FHIRValidationError as e:
            self.__set_unsuccesful_response(400, "value", "JSON_PAYLOAD_NOT_VALID_TO_SCHEMA",
                                            str(e.args[0]))

    @timing.time_request
    async def patch(self, patient_id):
        self.set_status(202)
        await self.finish(f'Amendment for patient `{patient_id}')
