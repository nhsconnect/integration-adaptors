import json
import os
from pathlib import Path

from jsonschema import Draft6Validator, ValidationError

import utilities.integration_adaptors_logger as log
from outbound.schema.schema_validation_exception import SchemaValidationException

_logger = log.IntegrationAdaptorsLogger(__name__)

_MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
_SCHEMAS_DIR = "schemas"
_SCHEMAS_PATH = str(Path(_MODULE_PATH) / _SCHEMAS_DIR)


def _load_schema(json_schema_filename):
    full_path = Path(_SCHEMAS_PATH) / json_schema_filename
    with open(full_path) as file:
        return json.load(file)


def _create_validator(json_schema_file):
    schema_json = _load_schema(json_schema_file)
    return Draft6Validator(schema_json)


_PATIENT_VALIDATOR = _create_validator('json-schema-patient.json')


def validate_patient(request_body):
    try:
        _PATIENT_VALIDATOR.validate(instance=request_body)
        __validate_patient_id_exists_in_payload(request_body)
    except ValidationError as e:
        raise SchemaValidationException(message=e.message, path=e.path)


def __validate_patient_id_exists_in_payload(request_body):
    if 'id' not in request_body:
        raise SchemaValidationException(message="id is missing from payload.", path="id")
