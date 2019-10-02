import logging
import os
import ssl
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line
from fake_spine.certs import Certs
from fake_spine.request_handler import SpineRequestHandler
from fake_spine.request_matcher_wrappers import body_contains_message_id, ebxml_body_contains_message_id
from fake_spine.request_matching import SpineRequestResponseMapper, RequestMatcher
from fake_spine.spine_response import SpineResponse

logger = logging.getLogger(__name__)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_application(fake_response_handler: SpineRequestResponseMapper):
    return tornado.web.Application([
        (r"/", SpineRequestHandler, dict(fake_response_handler=fake_response_handler)),
    ])


def build_application_configuration() -> SpineRequestResponseMapper:
    return SpineRequestResponseMapper({
        RequestMatcher('soap-fault-response', lambda x: ebxml_body_contains_message_id(x.body.decode(), 'AD7D39A8-1B6C-4520-8367-6B7BEBD7B842')):
            SpineResponse().override_response_code(500).override_response('soap_fault_single_error.xml'),
        RequestMatcher('soap-fault-response', lambda x: body_contains_message_id(x.body.decode(), 'F5187FB6-B033-4A75-838B-9E7A1AFB3111')):
            SpineResponse().override_response_code(500).override_response('soap_fault_single_error.xml'),
        RequestMatcher('exml-fault-response', lambda x: ebxml_body_contains_message_id(x.body.decode(),'7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA')):
            SpineResponse().override_response_code(500).override_response('ebxml_fault_single_error.xml')
    })


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

    server.listen(443)
    logger.log(logging.INFO, "Starting fakespine service")
    tornado.ioloop.IOLoop.current().start()
