import json
from jsonschema import validate

import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

def validate_schema(request):
    requestBody = json.loads(request)
    schema = {
        'type': 'object',
        'properties': {
            'payload': {'type': 'string'},
            'address': {
                'id': 'string',
                'use': 'string'
            }
        },
    }

    is_valid_schema = False

    try:
        validate(instance=requestBody, schema=schema)
        is_valid_schema = True
    except Exception:
        logger.critical('Did not match json schema')

    return is_valid_schema

