"""This module defines the outbound transmission component."""

import asyncio
from ssl import SSLError
from typing import Dict

from mhs_common.transmission import transmission_adaptor
from tornado import httpclient

from comms.common_https import CommonHttps
from exceptions import MaxRetriesExceeded
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger("OUTBOUND_TRANSMISSION")


class OutboundTransmission(transmission_adaptor.TransmissionAdaptor):
    errors_not_to_retry = [
        httpclient.HTTPClientError,
        SSLError
    ]

    """A component that sends HTTP requests to a remote MHS."""

    def __init__(self, client_cert: str, client_key: str, ca_certs: str, max_retries: int,
                 retry_delay: int, http_proxy_host: str = None, http_proxy_port: int = None):
        """Create a new OutboundTransmission that loads certificates from the specified directory.

        :param client_cert: A string containing the filepath of the client certificate file.
        :param client_key: A string containing the filepath of the client private key file.
        :param ca_certs: A string containing the filepath of the certificate authority certificate file.
        :param max_retries: An integer with the value of the max number times to retry sending the request.
        :param retry_delay: An integer representing the delay (in milliseconds) to use between retry attempts.
        :param http_proxy_host The hostname of the HTTP proxy to be used.
        :param http_proxy_port The port of the HTTP proxy to be used.
        """
        self._client_cert = client_cert
        self._client_key = client_key
        self._ca_certs = ca_certs
        self._max_retries = max_retries
        self._retry_delay = retry_delay

        self._proxy_host = http_proxy_host
        self._proxy_port = http_proxy_port

    async def make_request(self, url: str, headers: Dict[str, str], message: str) -> httpclient.HTTPResponse:

        request_method = "POST"

        retries_remaining = self._max_retries
        while True:
            try:
                logger.info("0001", "About to send message with {headers} to {url} using {proxy_host} & {proxy_port}",
                            {"headers": headers, "url": url, "proxy_host": self._proxy_host,
                             "proxy_port": self._proxy_port})
                # ******************************************************************************************************
                # TLS CERTIFICATE VALIDATION HAS BEEN TEMPORARILY DISABLED! This is required because Opentest's SDS
                # instance currently returns endpoints as IP addresses. This MUST be changed before this code is used in
                # a production environment
                # ******************************************************************************************************
                response = await CommonHttps.make_request(url=url, method=request_method, headers=headers, body=message,
                                                          client_cert=self._client_cert, client_key=self._client_key,
                                                          ca_certs=self._ca_certs, validate_cert=False,
                                                          http_proxy_host=self._proxy_host,
                                                          http_proxy_port=self._proxy_port)
                logger.info("0002", "Sent message with {headers} to {url} using {proxy_host} & {proxy_port} and "
                                    "received status code {code}",
                            {"headers": headers, "url": url, "proxy_host": self._proxy_host,
                             "proxy_port": self._proxy_port, "code": response.code})
                return response
            except Exception as e:
                if not self._is_retriable(e):
                    raise e

                retries_remaining -= 1
                logger.warning("0003",
                               "A retriable error was encountered {exception} {retries_remaining} {max_retries}",
                               {"exception": e,
                                "retries_remaining": retries_remaining,
                                "max_retries": self._max_retries
                                })
                if retries_remaining <= 0:
                    logger.error("0004",
                                 "A request has exceeded the maximum number of retries, {max_retries} retries",
                                 {"max_retries": self._max_retries})
                    raise MaxRetriesExceeded("The max number of retries to make a request has been exceeded") from e

                logger.info("0005", "Waiting for {retry_delay} milliseconds before next request attempt.",
                            {"retry_delay": self._retry_delay})
                await asyncio.sleep(self._retry_delay / 1000)

    def _is_tornado_network_error(self, e):
        return isinstance(e, httpclient.HTTPClientError) and e.code == 599

    def _is_retriable(self, e):
        if self._is_tornado_network_error(e):
            return True

        for error_type in self.errors_not_to_retry:
            if isinstance(e, error_type):
                return False

        return True
