import json
from json import JSONDecodeError
from typing import Any

import tornado.web
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.operationoutcome import OperationOutcome
from fhir.resources.operationoutcome import OperationOutcomeIssue
from tornado import httputil
from utilities import integration_adaptors_logger as log, timing
from utilities import message_utilities

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.fhir_to_edifact import FhirToEdifact
from outbound.schema import validate_request
from outbound.schema.request_validation_exception import RequestValidationException

logger = log.IntegrationAdaptorsLogger(__name__)


class AcceptanceAmendmentRequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self.fhir_to_edifact = FhirToEdifact()
        self.mesh_wrapper = MeshOutboundWrapper()

    def __set_unsuccesful_response(self, status, code, coding_code, details):
        self.set_status(status)

        coding = Coding()
        coding.code = coding_code
        coding.display = details
        coding.version = '1'
        coding.system = 'https://www.hl7.org/fhir/patient.html'

        details = CodeableConcept()
        details.coding = [coding]  # don't need coding
        details.text  # message goes here

        # TODO: now that RequestValidationException has a list of errors we need to map that to a list of issues
        #  OperationOutcomeIssue has a location property that should be used for the path (JSONPath) of the error
        #  details is a CodeableConcept object. The error message should be the text property of the CodeableConcept
        #  http://www.hl7.org/fhir/operationoutcome-example-validationfail.json.html - don't do the 'text' bit this is for interactive web apps
        #  http://www.hl7.org/fhir/operationoutcome.html
        operation_outcome_issue = OperationOutcomeIssue()
        operation_outcome_issue.severity = 'error'
        operation_outcome_issue.code = code
        operation_outcome_issue.details = details
        operation_outcome_issue.expression  # path goes here

        operation_outcome = OperationOutcome()
        operation_outcome.issue = [operation_outcome_issue]

        self.finish(operation_outcome.as_json())

    @timing.time_request
    async def post(self, patient_id):
        try:
            request_body = json.loads(self.request.body.decode())
            patient = validate_request.validate_patient(request_body)
            if patient.id == patient_id:
                edifact = self.fhir_to_edifact.convert(patient)
                unique_operation_id = message_utilities.get_uuid()
                await self.mesh_wrapper.send(edifact.as_json())
                self.set_status(202)
                self.set_header("OperationId", unique_operation_id)
                await self.finish()
            else:
                self.__set_unsuccesful_response(400, "value", "ID_IN_URI_DOES_NOT_MATCH_PAYLOAD_ID",
                                                f"URI id `{patient_id}` does not match PAYLOAD id `{patient.id}`")
                logger.error('Error, id doesnt match')
        except RequestValidationException as e:
            details = f"{e.path} {e.message}"
            self.__set_unsuccesful_response(400, "value", "JSON_PAYLOAD_NOT_VALID_TO_SCHEMA", details)
            logger.error(f'Error: {details}')
        except JSONDecodeError as e:
            self.__set_unsuccesful_response(400, "value", "PAYLOAD_IS_NOT_VALID_JSON_FORMAT",
                                            "Payload is either missing, empty or not valid to json, this is required.")
            logger.error('Error: Payload is missing, empty or not a valid json')

    @timing.time_request
    async def patch(self, patient_id):
        self.set_status(202)
        await self.finish(f'Amendment for patient `{patient_id}')
