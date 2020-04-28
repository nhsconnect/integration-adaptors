import json
from json import JSONDecodeError
from typing import Any

import tornado.web
from fhir.resources.codeableconcept import CodeableConcept
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

    def __set_unsuccesful_response(self, status, code, path, message):
        operation_outcome = self.__build_operation_outcome(code, path, message)
        self.set_status(status)
        self.finish(operation_outcome.as_json())

    def __build_operation_outcome(self, code, path, message):
        details = CodeableConcept()
        details.text = message

        operation_outcome_issue = OperationOutcomeIssue()
        operation_outcome_issue.severity = 'error'
        operation_outcome_issue.code = code
        operation_outcome_issue.details = details
        operation_outcome_issue.expression = path

        operation_outcome = OperationOutcome()
        operation_outcome.id = "validationfail"
        operation_outcome.issue = [operation_outcome_issue]

        return operation_outcome
        
    def __extract_request_validateion_path_and_message(self, errors):
        path_list = []
        message_list_string = ''

        for path, message in errors:
            path_list.append(path)
            message_list_string += f'{message} \n '

        return path_list, message_list_string

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
                logger.exception('Exception, id doesnt match')
                self.__set_unsuccesful_response(400, "value", ["id"],
                                                f"URI id `{patient_id}` does not match PAYLOAD id `{patient.id}`")
        except RequestValidationException as e:
            details = self.__extract_request_validateion_path_and_message(e.errors)
            logger.exception(f'Exception: {details}')
            self.__set_unsuccesful_response(400, "value", details[0], details[1])
        except JSONDecodeError as e:
            logger.exception('Exception: Payload is missing, empty or not a valid json')
            self.__set_unsuccesful_response(400, "value", ["PAYLOAD"],
                                            "Payload is either missing, empty or not valid to json, this is required.")
        except Exception as e:
            logger.exception(f'Exception: {e}')
            self.set_status(500)

    @timing.time_request
    async def patch(self, patient_id):
        self.set_status(202)
        await self.finish(f'Amendment for patient `{patient_id}')
