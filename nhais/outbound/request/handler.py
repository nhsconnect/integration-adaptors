import json
from typing import Any

from fhir.resources.patient import Patient
from tornado import httputil

from common.handler import base_handler
from comms import proton_queue_adaptor
from mesh.mesh_outbound import MeshOutboundWrapper
from outbound.converter.interchange_translator import InterchangeTranslator
from utilities import config
from utilities import integration_adaptors_logger as log, timing

logger = log.IntegrationAdaptorsLogger(__name__)


class Handler(base_handler.BaseHandler):

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
            urls=[config.get_config('OUTBOUND_QUEUE_HOST')],
            username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
            password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None),
            queue='mesh_outbound')
        self.fhir_to_edifact = InterchangeTranslator()
        self.mesh_wrapper = MeshOutboundWrapper(queue_adaptor)

    @timing.time_request
    async def post(self):
        body = self.request.body.decode()
        body_json = json.loads(body)
        patient = Patient(body_json)
        edifact = await self.fhir_to_edifact.convert(patient)
        await self.mesh_wrapper.send(edifact)
        self.set_status(202)
