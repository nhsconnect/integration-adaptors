import logging
import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.web
from tornado.options import parse_command_line
from fake_spineroutelookup.request_handler import RoutingRequestHandler
from fake_spineroutelookup.request_matching import SpineRouteLookupRequestResponseMapper, RequestMatcher
from fake_spineroutelookup.request_matcher_wrappers import query_argument_contains_string
from fake_spineroutelookup.routing_response import RoutingResponse

logger = logging.getLogger(__name__)


def build_application(fake_response_handler: SpineRouteLookupRequestResponseMapper):
    return tornado.web.Application([
        (r"/routing", RoutingRequestHandler, dict(fake_response_handler=fake_response_handler)),
    ])


def build_application_configuration() -> SpineRouteLookupRequestResponseMapper:
    return SpineRouteLookupRequestResponseMapper({
        RequestMatcher(
            'routing-QUPA_IN040000UK32',
            lambda x: query_argument_contains_string(x, "service-id", "QUPA_IN040000UK32")): RoutingResponse()
    })


if __name__ == "__main__":
    parse_command_line()

    logger.log(logging.INFO, "Building fake spineroutelookup service configuration")

    application_configuration = build_application_configuration()
    application = build_application(application_configuration)
    server = tornado.httpserver.HTTPServer(application)
    server.listen(80)

    logger.log(logging.INFO, "Starting fake spineroutelookup service")
    tornado.ioloop.IOLoop.current().start()
