import json
from jsonschema import validate
import os

import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

def validate_schema(request):
    request_body = json.loads(request)

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    json_schema_patient = ROOT_DIR + "/json-schema-patient.json"



    with open(json_schema_patient) as file:
        data = json.load(file)

    is_valid_schema = False

    try:
        validate(instance=request_body, schema=data)
        is_valid_schema = True
    except Exception:
        logger.critical('Did not match json schema')

    return is_valid_schema

