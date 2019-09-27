import json

import apispec
import apispec.ext.marshmallow
import apispec_webframeworks.tornado
from mhs_common.request import healthcheck_handler

from outbound.request import request_body_schema
from outbound.request.synchronous import handler


def create_spec() -> apispec.APISpec:
    """
    Create an `APISpec` that documents the MHS API
    :return: the `APISpec` that documents the MHS API
    """
    spec = apispec.APISpec(
        title='MHS API docs',
        version='0.1',
        openapi_version='3.0.2',
        plugins=[apispec.ext.marshmallow.MarshmallowPlugin(), apispec_webframeworks.tornado.TornadoPlugin()]
    )

    spec.components.schema("RequestBody", schema=request_body_schema.RequestBodySchema)

    # The paths here should match the paths in main.py
    spec.path(urlspec=(r'/', handler.SynchronousHandler))
    spec.path(urlspec=(r'/healthcheck', healthcheck_handler.HealthcheckHandler))

    return spec


if __name__ == '__main__':
    print(json.dumps(create_spec().to_dict()))
