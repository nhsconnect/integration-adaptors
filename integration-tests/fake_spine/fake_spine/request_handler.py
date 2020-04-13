import asyncio
from utilities import integration_adaptors_logger as log

import tornado.web

from fake_spine.inbound_client import InboundClient
from fake_spine.request_matching import SpineRequestResponseMapper
from fake_spine.spine_responses import InboundRequest
from fake_spine import fake_spine_configuration

logger = log.IntegrationAdaptorsLogger(__name__)


class SpineRequestHandler(tornado.web.RequestHandler):

    def initialize(self, fake_response_handler: SpineRequestResponseMapper) -> None:
        self.fake_response_handler = fake_response_handler
        self.inbound_client = InboundClient()
        self.config = fake_spine_configuration.FakeSpineConfiguration()

    async def _do_outbound_delay(self):
        logger.debug(f'Delaying outbound response by {self.config.OUTBOUND_DELAY_MS}ms')
        await asyncio.sleep(self.config.OUTBOUND_DELAY_MS / 1000.0)

    async def _do_inbound_request(self, inbound_request: InboundRequest):
        logger.debug(f'Delaying inbound request by {self.config.INBOUND_DELAY_MS}ms')
        await asyncio.sleep(self.config.INBOUND_DELAY_MS / 1000.0)
        await self.inbound_client.make_request(inbound_request)

    async def post(self):
        logger.info(f"request accepted {self.request} with headers: {self.request.headers}, and body: {self.request.body}")
        responses = self.fake_response_handler.response_for_request(self.request)
        status, response = responses.get_outbound_response(self.request)
        logger.info(f"response to request {status} : {response}")

        await self._do_outbound_delay()

        self.set_header('Content-Type', 'text/xml')
        self.set_status(status)
        self.write(response)

        # fire-and-forget the inbound request to allow it to happen some time after the outbound request completes
        inbound_request = responses.get_inbound_request(self.request)
        if inbound_request:
            asyncio.ensure_future(self._do_inbound_request(inbound_request))
