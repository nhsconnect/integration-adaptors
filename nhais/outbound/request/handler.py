from typing import Any

from comms import proton_queue_adaptor
from tornado import httputil
from common.handler import base_handler

from utilities import integration_adaptors_logger as log, timing
from utilities import config

from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.base_translator import BaseFhirToEdifactTranslator

logger = log.IntegrationAdaptorsLogger(__name__)


class Handler(base_handler.BaseHandler):

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
            host=config.get_config('OUTBOUND_QUEUE_HOST'),
            username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
            password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None))
        self.fhir_to_edifact = BaseFhirToEdifactTranslator()
        self.mesh_wrapper = MeshOutboundWrapper(queue_adaptor)

    @timing.time_request
    async def post(self):
        edifact = self.fhir_to_edifact.convert(self.request.body.decode())
        await self.mesh_wrapper.send(edifact)
        self.set_status(202)
