import logging
import tornado
from request_matching import SpineRequestResponseMapper

logger = logging.getLogger(__name__)


class RoutingRequestHandler(tornado.web.RequestHandler):

    def initialize(self, fake_response_handler: SpineRequestResponseMapper) -> None:
        self.fake_response_handler = fake_response_handler

    async def post(self):
        logger.log(logging.INFO, f"request accepted {self.request} with headers: {self.request.headers}")
        status, response = self.fake_response_handler.response_for_request(self.request)
        logger.log(logging.INFO, f"response to request {status} : {response}")

        self.set_header('Content-Type', 'text/xml')
        self.set_status(status)
        self.write(response)
