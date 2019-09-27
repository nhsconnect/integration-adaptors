import logging
import ssl
import os
from typing import Callable, Dict

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.httputil import HTTPServerRequest
from tornado.options import parse_command_line
from certs import Certs


class RoutingResponse(object):

    def __init__(self):
        self.response_file_location = None
        self.response_code = 200

    def override_response(self, response_file_location: str):
        self.response_file_location = response_file_location
        return self

    def override_response_code(self, response_code: int):
        self.response_code = response_code
        return self

    def get_response(self):
        


class RequestMatcher(object):

    def __init__(self, matcher: Callable[[HTTPServerRequest], bool]):
        self.matcher = matcher

    def does_match(self, request: HTTPServerRequest) -> bool:
        return self.matcher(request)


class SpineRequestResponseMapper(object):

    def __init__(self, request_matcher_to_response: Dict[RequestMatcher, RoutingResponse]):
        self.request_matcher_to_response = request_matcher_to_response

    def response_for_request(self, request: HTTPServerRequest) -> dict:
        for request_matcher, response in self.request_matcher_to_response.items():
            matches_response = request_matcher.does_match(request)
            if matches_response:
                logger.log(logging.INFO, "request matched a configured matcher")
                return response.get_response()

        logger.log(logging.ERROR,
                   f"no matcher configured that matched request {request} with headers: {request.headers}")
        raise Exception(f"no response configured matching the request")


class RoutingRequestHandler(tornado.web.RequestHandler):

    def initialize(self, fake_response_handler: SpineRouteLookupRequestResponseMapper) -> None:
        self.fake_response_handler = fake_response_handler

    async def get(self):
        logger.log(logging.INFO, f"request accepted {self.request} with headers: {self.request.headers}")
        response = self.fake_response_handler.response_for_request(self.request)
        logger.log(logging.INFO, f"response to request {response}")

        self.write(response)


logger = logging.getLogger(__name__)


def build_application(fake_response_handler: SpineRequestResponseMapper):
    return tornado.web.Application([
        (r"/routing", RoutingRequestHandler, dict(fake_response_handler=fake_response_handler)),
    ])


def build_application_configuration() -> SpineRequestResponseMapper:
    return SpineRequestResponseMapper({
        RequestMatcher(
            lambda x: query_argument_contains_string(x, "service-id", "QUPA_IN040000UK32")): RoutingResponse()
    })


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    parse_command_line()

    certs = Certs.create_certs_files(ROOT_DIR,
                                     private_key=os.environ.get('FAKE_SPINE_PRIVATE_KEY'),
                                     local_cert=os.environ.get('FAKE_SPINE_PUBLIC_KEY'),
                                     ca_certs=os.environ.get('FAKE_SPINE_CA_CERTS'))

    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(certs.local_cert_path, certs.private_key_path)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.load_verify_locations(certs.ca_certs_path)

    application = build_application()
    server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx)

    server.listen(443)
    tornado.ioloop.IOLoop.current().start()
