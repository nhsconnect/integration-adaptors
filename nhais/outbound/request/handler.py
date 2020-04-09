from typing import Any

from comms import proton_queue_adaptor
from comms.http_headers import HttpHeaders
from tornado import httputil
from utilities import mdc
from common.handler import base_handler

from utilities import integration_adaptors_logger as log, message_utilities, timing

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.fhir_to_edifact import FhirToEdifact

logger = log.IntegrationAdaptorsLogger(__name__)


class Handler(base_handler.BaseHandler):

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self.super(application, request, kwargs)
        self.fhir_to_edifact = FhirToEdifact()
        queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
            host="localhost:5672/outbound",
            username=None,
            password=None)
        self.mesh_wrapper = MeshOutboundWrapper(queue_adaptor)

    @timing.time_request
    async def post(self):
        edifact = self.fhir_to_edifact.convert(self.request.body.decode())
        await self.mesh_wrapper.send(edifact)

        self.set_status(202)
        # TODO: response status code 202
        test_id = self._extract_test_id()


    def _extract_test_id(self):
        message_id = self.request.headers.get(HttpHeaders.TEST_ID, None)
        if not message_id:
            message_id = message_utilities.MessageUtilities.get_uuid()
            mdc.message_id.set(message_id)
            logger.info("Didn't receive message id in incoming request from supplier, so have generated a new one.")
        else:
            mdc.message_id.set(message_id)
            logger.info('Found message id on incoming request.')
        return message_id