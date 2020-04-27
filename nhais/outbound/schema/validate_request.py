import utilities.integration_adaptors_logger as log
from fhir.resources.fhirabstractbase import FHIRValidationError
from fhir.resources.fhirelementfactory import FHIRElementFactory
from jsonschema import ValidationError

from outbound.schema.request_validation_exception import RequestValidationException

_logger = log.IntegrationAdaptorsLogger(__name__)


def validate_patient(request_body):
    try:
        patient = FHIRElementFactory.instantiate('Patient', request_body)
        __validate_patient_id_exists_in_payload(request_body)
    except FHIRValidationError as e:
        raise RequestValidationException(message=e.args[0], path=e.errors[0].args[0][:e.errors[0].args[0].index(":")])
    return patient


def __validate_patient_id_exists_in_payload(request_body):
    if 'id' not in request_body:
        raise RequestValidationException(message="id is missing from payload.", path="id")
