from fhir.resources.fhirabstractbase import FHIRValidationError
from jsonschema import ValidationError

from fhir.resources.fhirelementfactory import FHIRElementFactory

import utilities.integration_adaptors_logger as log
from outbound.schema.schema_validation_exception import SchemaValidationException

_logger = log.IntegrationAdaptorsLogger(__name__)


def validate_patient(request_body):
    try:
        patient = FHIRElementFactory.instantiate('Patient', request_body)
        __validate_patient_id_exists_in_payload(request_body)
    except ValidationError as e:
        raise SchemaValidationException(message=e.message, path=e.path)
    except FHIRValidationError as e:
        raise FHIRValidationError(e.args[0])
    return patient


def __validate_patient_id_exists_in_payload(request_body):
    if 'id' not in request_body:
        raise SchemaValidationException(message="id is missing from payload.", path="id")
