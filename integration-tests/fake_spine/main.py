import logging
import os
import ssl

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line

from fake_spine.certs import Certs
from fake_spine.component_test_responses import component_test_responses
from fake_spine.inbound_proxy_request_handler import InboundProxyRequestHandler
from fake_spine.request_handler import SpineRequestHandler
from fake_spine.request_matching import SpineRequestResponseMapper

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
    # TODO: Add V&P response mappings
    # Now that the mappings are stored in a List instead of a dict they can be ordered
    # The component tests all match requests using UUID message ids. These matchers should run first
    # The V&P matchers will use the SOAPAction or other indication of request type. The response will parse the
    #   message id and other relevant data from the request to build a response from a template
    return SpineRequestResponseMapper(response_mappings)


if __name__ == "__main__":
    parse_command_line()

    logger.log(logging.INFO, "Building fakespine service configuration")

    certs = Certs.create_certs_files(ROOT_DIR,
                                     private_key=os.environ.get('FAKE_SPINE_PRIVATE_KEY'),
                                     local_cert=os.environ.get('FAKE_SPINE_CERTIFICATE'),
                                     ca_certs=os.environ.get('FAKE_SPINE_CA_STORE'))

    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(certs.local_cert_path, certs.private_key_path)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.load_verify_locations(certs.ca_certs_path)

    application_configuration = build_application_configuration()
    application = build_application(application_configuration)

    server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_ctx)
    fake_spine_port = os.environ.get('FAKE_SPINE_PORT', default='443')
    logger.info('Fake spine starting on port %s', fake_spine_port)
    server.listen(int(fake_spine_port))

    proxy_application = build_proxy_application(certs)
    proxy = tornado.httpserver.HTTPServer(proxy_application)
    inbound_proxy_port = os.environ.get('INBOUND_PROXY_PORT', default='80')
    logger.info('Inbound proxy starting on port %s', inbound_proxy_port)
    proxy.listen(int(inbound_proxy_port))

    logger.log(logging.INFO, "Starting fakespine service")
    tornado.ioloop.IOLoop.current().start()
