import logging
import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.web
import os
from tornado.options import parse_command_line
from fake_spineroutelookup.request_handler import RoutingRequestHandler
from fake_spineroutelookup.request_matching import SpineRouteLookupRequestResponseMapper, RequestMatcher
from fake_spineroutelookup.request_matcher_wrappers import query_argument_contains_string
from fake_spineroutelookup.routing_response import RoutingResponse
from fake_spineroutelookup.reliability_response import ReliabilityResponse

logger = logging.getLogger(__name__)


def build_application(fake_routing_response_handler: SpineRouteLookupRequestResponseMapper,
                      fake_reliability_response_handler: SpineRouteLookupRequestResponseMapper
                      ):
    return tornado.web.Application([
        (r"/routing", RoutingRequestHandler, dict(fake_response_handler=fake_routing_response_handler)),
        (r"/reliability", RoutingRequestHandler, dict(fake_response_handler=fake_reliability_response_handler))
    ])


def build_routing_configuration() -> SpineRouteLookupRequestResponseMapper:
    return SpineRouteLookupRequestResponseMapper({
        RequestMatcher(
            'routing-QUPA_IN040000UK32',
            lambda x: query_argument_contains_string(x, "service-id", "QUPA_IN040000UK32")): RoutingResponse(),

        RequestMatcher(
            'routing-QUPC_IN160101UK05',
            lambda x: query_argument_contains_string(x, 'service-id', 'QUPC_IN160101UK05')): RoutingResponse(),

        RequestMatcher(
            'routing-REPC_IN150016UK05',
            lambda x: query_argument_contains_string(x, 'service-id', 'REPC_IN150016UK05')): RoutingResponse(),
        RequestMatcher(
            'routing-COPC_IN000001UK01',
            lambda x: query_argument_contains_string(x, 'service-id', 'COPC_IN000001UK01')): RoutingResponse(),
        RequestMatcher(
            'routing-PRSC_IN080000UK07',
            lambda x: query_argument_contains_string(x, 'service-id', 'PRSC_IN080000UK07')): RoutingResponse()
    })


def build_reliability_configuration() -> SpineRouteLookupRequestResponseMapper:
    return SpineRouteLookupRequestResponseMapper({
        RequestMatcher(
            'reliability-REPC_IN150016UK05',
            lambda x: query_argument_contains_string(x, "service-id", "REPC_IN150016UK05")): ReliabilityResponse(),

        RequestMatcher(
            'reliability-COPC_IN000001UK01',
            lambda x: query_argument_contains_string(x, "service-id", "COPC_IN000001UK01")): ReliabilityResponse(),
        RequestMatcher(
            'reliability-PRSC_IN080000UK07',
            lambda x: query_argument_contains_string(x, 'service-id', 'PRSC_IN080000UK07')): ReliabilityResponse()
    })


if __name__ == "__main__":
    parse_command_line()

    logger.log(logging.INFO, "Building fake spineroutelookup service configuration")

    routing_configuration = build_routing_configuration()
    reliability_configuration = build_reliability_configuration()
    application = build_application(routing_configuration, reliability_configuration)
    server = tornado.httpserver.HTTPServer(application)
    spine_route_lookup_port = os.environ.get('SPINE_ROUTE_LOOKUP_PORT', default='80')
    logger.info('Fake spine route lookup starting on port %s', spine_route_lookup_port)
    server.listen(int(spine_route_lookup_port))

    logger.log(logging.INFO, "Starting fake spineroutelookup service")
    tornado.ioloop.IOLoop.current().start()
