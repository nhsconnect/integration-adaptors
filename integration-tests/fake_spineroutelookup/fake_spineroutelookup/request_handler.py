import logging
import tornado.web
from fake_spineroutelookup.request_matching import SpineRouteLookupRequestResponseMapper

logger = logging.getLogger(__name__)


class RoutingRequestHandler(tornado.web.RequestHandler):

    def initialize(self, fake_response_handler: SpineRouteLookupRequestResponseMapper) -> None:
        self.fake_response_handler = fake_response_handler

    async def get(self):
        logger.log(logging.INFO, f"request accepted {self.request} with headers: {self.request.headers}")
        response = self.fake_response_handler.response_for_request(self.request)
        logger.log(logging.INFO, f"response to request {response}")

        self.write(response)
