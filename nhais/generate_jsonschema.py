import json
from jsonschema import validate

import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

def validate_schema(request_body, json_schema_patient):

    with open(json_schema_patient) as file:
        data = json.load(file)

    try:
        validate(instance=request_body, schema=data)
        return None
    except Exception as e:
        logger.error('Did not match json schema' + str(e))
        return e
