import json
from jsonschema import validate
import os

import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

def validate_schema(request_body):

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    json_schema_patient = ROOT_DIR + "/json-schema-patient.json"

    with open(json_schema_patient) as file:
        data = json.load(file)

    exception_thrown = None

    try:
        validate(instance=request_body, schema=data)
    except Exception as e:
        logger.error('Did not match json schema' + str(e))
        exception_thrown = e


    return exception_thrown
