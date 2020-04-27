from typing import Any

from tornado import httputil

from common.handler import base_handler
from comms import proton_queue_adaptor
from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.interchange_translator import FhirToEdifactTranslator
from utilities import config
from utilities import integration_adaptors_logger as log, timing

logger = log.IntegrationAdaptorsLogger(__name__)


class Handler(base_handler.BaseHandler):

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
            host=config.get_config('OUTBOUND_QUEUE_HOST'),
            username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
            password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None))
        self.fhir_to_edifact = FhirToEdifactTranslator()
        self.mesh_wrapper = MeshOutboundWrapper(queue_adaptor)

    @timing.time_request
    async def post(self):
        edifact = self.fhir_to_edifact.convert(self.request.body.decode())
        await self.mesh_wrapper.send(edifact)
        self.set_status(202)
