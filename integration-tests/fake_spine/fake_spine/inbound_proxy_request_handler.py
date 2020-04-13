from utilities import integration_adaptors_logger as log

import tornado.web
from tornado import httpclient

from fake_spine.certs import Certs
from fake_spine import fake_spine_configuration

logger = log.IntegrationAdaptorsLogger(__name__)


class InboundProxyRequestHandler(tornado.web.RequestHandler):

    def initialize(self, inbound_certs: Certs) -> None:
        self.inbound_certs = inbound_certs
        self.config = fake_spine_configuration.FakeSpineConfiguration()

    async def post(self):
        logger.info(f"request accepted {self.request} with headers: {self.request.headers}, and body: {self.request.body}")
        logger.info(f"request being proxied to inbound service")

        response = await httpclient.AsyncHTTPClient()\
            .fetch(self.config.INBOUND_SERVER_BASE_URL,
                   raise_error=False,
                   method="POST",
                   body=self.request.body,
                   headers=self.request.headers,
                   client_cert=self.inbound_certs.local_cert_path,
                   client_key=self.inbound_certs.private_key_path,
                   ca_certs=self.inbound_certs.ca_certs_path,
                   validate_cert=self.config.FAKE_SPINE_PROXY_VALIDATE_CERT)

        logger.info(f"inbound responded with code: {response.code} and body: {response.body}")
        self.set_status(response.code)
        self.write(response.body)
