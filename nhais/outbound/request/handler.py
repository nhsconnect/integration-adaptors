from typing import Any

from comms import proton_queue_adaptor
from tornado import httputil
from common.handler import base_handler

from utilities import integration_adaptors_logger as log, timing
from utilities import config, message_utilities

import generate_openapi

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.fhir_to_edifact import FhirToEdifact

logger = log.IntegrationAdaptorsLogger(__name__)


class Handler(base_handler.BaseHandler):

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
            host=config.get_config('OUTBOUND_QUEUE_HOST'),
            username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
            password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None))
        self.fhir_to_edifact = FhirToEdifact()
        self.mesh_wrapper = MeshOutboundWrapper(queue_adaptor)

    @timing.time_request
    async def post(self):
        is_valid_schema = generate_openapi.validate_schema(self.request.body.decode())
        if(is_valid_schema):
            edifact = self.fhir_to_edifact.convert(self.request.body.decode())
            unique_operation_id = message_utilities.get_uuid()
            await self.mesh_wrapper.send(edifact)
            self.set_status(202)
            self.finish(f"<html><body>UniqueOperationID: {unique_operation_id}</body></html>")
        else:
            self.set_status(400)
            self.finish("<html><body>Resource could not be parsed or failed basic FHIR validation rules (or multiple matches were found for conditional criteria)</body></html>")
