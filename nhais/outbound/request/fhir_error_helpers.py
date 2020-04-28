import enum

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue

from outbound.schema.request_validation_exception import RequestValidationException, ValidationError


class OperationOutcomeIssueCode(enum.Enum):
    STRUCTURE = 'structure'
    URI = 'uri'


def create_operation_outcome(code: OperationOutcomeIssueCode, path: str, message: str):
    operation_outcome = OperationOutcome()
    operation_outcome.id = 'validationfail'
    operation_outcome.issue = [__operation_outcome_issue(code, path, message)]
    return operation_outcome


def create_operation_outcome_from_validation_exception(exception: RequestValidationException) -> OperationOutcome:
    operation_outcome = OperationOutcome()
    operation_outcome.id = 'validationfail'
    issues = [__operation_outcome_issue_from_validation_error(error) for error in exception.errors]
    operation_outcome.issue = issues
    return operation_outcome


def __operation_outcome_issue_from_validation_error(error: ValidationError):
    return __operation_outcome_issue(code=OperationOutcomeIssueCode.STRUCTURE, path=error.path, message=error.message)


def __operation_outcome_issue(code: OperationOutcomeIssueCode, path: str, message: str):
    operation_outcome_issue = OperationOutcomeIssue()
    operation_outcome_issue.severity = 'error'
    operation_outcome_issue.code = code.value
    details = CodeableConcept()
    details.text = message
    operation_outcome_issue.details = details
    operation_outcome_issue.expression = [path]
    return operation_outcome_issue