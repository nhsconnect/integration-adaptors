import logging
import os
import ssl

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line

from fake_spine import config, healthcheck_handler
from fake_spine.certs import Certs
from fake_spine.component_test_responses import component_test_responses
from fake_spine.inbound_proxy_request_handler import InboundProxyRequestHandler
from fake_spine.request_handler import SpineRequestHandler
from fake_spine.request_matching import SpineRequestResponseMapper
from fake_spine.vnp_test_responses import vnp_test_responses

logger = logging.getLogger(__name__)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_proxy_application(inbound_certs: Certs):
    return tornado.web.Application([
        (r"/inbound-proxy", InboundProxyRequestHandler, dict(inbound_certs=inbound_certs)),
    ])


def build_application(fake_response_handler: SpineRequestResponseMapper):
    return tornado.web.Application([
        (r"/", SpineRequestHandler, dict(fake_response_handler=fake_response_handler)),
    ])


def build_application_configuration() -> SpineRequestResponseMapper:
    response_mappings = component_test_responses()
    response_mappings.extend(vnp_test_responses())
    return SpineRequestResponseMapper(response_mappings)


if __name__ == "__main__":
    parse_command_line()

    logger.log(logging.INFO, "Building fakespine service configuration")

    certs = Certs.create_certs_files(ROOT_DIR,
                                     private_key=config.FAKE_SPINE_PRIVATE_KEY,
                                     local_cert=config.FAKE_SPINE_CERTIFICATE,
                                     ca_certs=config.FAKE_SPINE_CA_STORE)

    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(certs.local_cert_path, certs.private_key_path)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.load_verify_locations(certs.ca_certs_path)

    application_configuration = build_application_configuration()
    application = build_application(application_configuration)

    server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx)
    logger.info(f'Fake spine starting on port {config.FAKE_SPINE_PORT}')
    server.listen(config.FAKE_SPINE_PORT)

    proxy_application = build_proxy_application(certs)
    proxy = tornado.httpserver.HTTPServer(proxy_application)
    logger.info(f'Inbound proxy starting on port {config.INBOUND_PROXY_PORT}')
    proxy.listen(config.INBOUND_PROXY_PORT)

    healthcheck_application = tornado.web.Application([
        ("/healthcheck", healthcheck_handler.HealthcheckHandler)
    ])
    logger.info(f'Healthcheck starting on port {config.FAKE_SPINE_HEALTHCHECK_PORT}')
    healthcheck_application.listen(config.FAKE_SPINE_HEALTHCHECK_PORT)

    logger.log(logging.INFO, "Starting fakespine service")
    tornado.ioloop.IOLoop.current().start()
