import json
from json import JSONDecodeError
from typing import Any

import tornado.web
from fhir.resources.operationoutcome import OperationOutcome
from tornado import httputil
from utilities import integration_adaptors_logger as log, timing
from utilities import message_utilities

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.fhir_to_edifact import FhirToEdifact
from outbound.request.fhir_error_helpers import create_operation_outcome_from_validation_exception, \
    OperationOutcomeIssueCode, create_operation_outcome
from outbound.schema import validate_request
from outbound.schema.request_validation_exception import RequestValidationException

logger = log.IntegrationAdaptorsLogger(__name__)


class AcceptanceAmendmentRequestHandler(tornado.web.RequestHandler):

    JSON_DECODE_ERROR_MESSAGE = "Request body is not parsable as JSON"
    URI_MISMATCH_ERROR = 'Identifier in URI does not match identifier in request body'

    def __init__(self, application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self.fhir_to_edifact = FhirToEdifact()
        self.mesh_wrapper = MeshOutboundWrapper()

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
                logger.error(self.URI_MISMATCH_ERROR)
                operation_outcome = create_operation_outcome(OperationOutcomeIssueCode.URI, 'id', self.URI_MISMATCH_ERROR)
                self.__set_unsuccessful_response(400, operation_outcome)

        except RequestValidationException as e:
            logger.exception(f'Error occurred when parsing the FHIR Patient payload')
            operation_outcome = create_operation_outcome_from_validation_exception(e)
            self.__set_unsuccessful_response(400, operation_outcome)
        except JSONDecodeError as e:
            logger.exception(self.JSON_DECODE_ERROR_MESSAGE)
            operation_outcome = create_operation_outcome(OperationOutcomeIssueCode.STRUCTURE, '', self.JSON_DECODE_ERROR_MESSAGE)
            self.__set_unsuccessful_response(400, operation_outcome)

    def __set_unsuccessful_response(self, status: int, operation_outcome: OperationOutcome):
        self.set_status(status)
        self.finish(operation_outcome.as_json())

    @timing.time_request
    async def patch(self, patient_id):
        self.set_status(202)
        await self.finish(f'Amendment for patient `{patient_id}')
