import utilities.integration_adaptors_logger as log
from fhir.resources.fhirabstractbase import FHIRValidationError
from fhir.resources.fhirelementfactory import FHIRElementFactory

from outbound.schema.request_validation_exception import RequestValidationException

_logger = log.IntegrationAdaptorsLogger(__name__)


def validate_patient(request_body):
    try:
        patient = FHIRElementFactory.instantiate('Patient', request_body)
        __validate_patient_id_exists_in_payload(request_body)
    except FHIRValidationError as e:
        errors = _parse_fhir_errors(e)
        raise RequestValidationException(message=errors[0][1], path=errors[0][0])
    return patient


def _parse_fhir_errors(e):

    errors = []

    def recurse(e, path):
        if hasattr(e, 'path') and e.path:
            if path:
                path = f'{path}.{e.path}'
            else:
                path = e.path
        if hasattr(e, 'errors') and e.errors:
            for child_error in e.errors:
                recurse(child_error, path)
        else:
            errors.append((path, e.args[0]))

    recurse(e, '')
    return errors


def __validate_patient_id_exists_in_payload(request_body):
    if 'id' not in request_body:
        raise RequestValidationException(message="id is missing from payload.", path="id")
