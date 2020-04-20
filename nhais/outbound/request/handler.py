from typing import Any

from comms import proton_queue_adaptor
from tornado import httputil
from common.handler import base_handler

from utilities import integration_adaptors_logger as log, timing
from utilities import config, message_utilities

import generate_jsonschema
import json

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

    def validate_uri_matches_payload_operation(self, request_body):
        operation = request_body['resourceType']
        request_uri = self.request.uri
        string_length_of_operation = request_uri.find(operation)
        if(string_length_of_operation >= len(operation)):
            return True
        else:
            return False

    @timing.time_request
    async def post(self):
        request_body = json.loads(self.request.body.decode())
        uri_matches_payload_operation = self.validate_uri_matches_payload_operation(request_body)
        if uri_matches_payload_operation:
            exception_thrown = generate_jsonschema.validate_schema(request_body)
            if exception_thrown is None:
                edifact = self.fhir_to_edifact.convert(self.request.body.decode())
                unique_operation_id = message_utilities.get_uuid()
                await self.mesh_wrapper.send(edifact)
                self.set_status(202)
                await self.finish(f"<html><body>UniqueOperationID: {unique_operation_id}</body></html>")
            else:
                self.set_status(400)
                await self.finish(
                    f"<html><body>Resource could not be parsed or failed basic FHIR validation rules (or multiple matches were found for conditional criteria). Details found below:\n\n{exception_thrown}</body></html>")
        else:
            self.set_status(400)
            await self.finish(
                f"<html><body>Requested uri operation: {self.request.uri}, does not match payload operation requested: {request_body['resourceType']}.</body></html>")
