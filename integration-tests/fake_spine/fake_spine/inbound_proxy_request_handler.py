import logging

import tornado.web
from tornado import httpclient

from fake_spine.certs import Certs
from fake_spine import config

logger = logging.getLogger(__name__)


class InboundProxyRequestHandler(tornado.web.RequestHandler):

    def initialize(self, inbound_certs: Certs) -> None:
        self.inbound_certs = inbound_certs

    async def post(self):
        logger.log(logging.INFO, f"request accepted {self.request} with headers: {self.request.headers}, and body: {self.request.body}")
        logger.log(logging.INFO, f"request being proxied to inbound service")

        response = await httpclient.AsyncHTTPClient()\
            .fetch(config.INBOUND_SERVER_BASE_URL,
                   raise_error=False,
                   method="POST",
                   body=self.request.body,
                   headers=self.request.headers,
                   client_cert=self.inbound_certs.local_cert_path,
                   client_key=self.inbound_certs.private_key_path,
                   ca_certs=self.inbound_certs.ca_certs_path,
                   validate_cert=True)

        logger.log(logging.INFO, f"inbound responded with code: {response.code} and body: {response.body}")
        self.set_status(response.code)
        self.write(response.body)
