"""This module defines the outbound transmission component."""

from pathlib import Path
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

    def __init__(self, certs_dir: str, client_cert: str, client_key: str, ca_certs: str, max_retries: int):
        """Create a new OutboundTransmission that loads certificates from the specified directory.
        :param certs_dir: A string containing the path to the directory to load certificates from.
        :param client_cert: A string containing the name of the client certificate file in the certs directory.
        :param client_key: A string containing the name of the client private key file in the certs directory.
        :param ca_certs: A string containing the name of the certificate authority certificate file in the certs directory.
        :param max_retries: An integer with the value of the max number times to retry sending the request.
        """
        self._client_cert = str(Path(certs_dir) / client_cert)
        self._client_key = str(Path(certs_dir) / client_key)
        self._ca_certs = str(Path(certs_dir) / ca_certs)
        self._max_retries = max_retries

    async def make_request(self, url: str, headers: Dict[str, str], message: str) -> httpclient.HTTPResponse:

        request_method = "POST"

        retries_remaining = self._max_retries
        while True:
            try:
                logger.info("0001", "About to send message with {headers} to {url} : {message}",
                            {"headers": headers, "url": url, "message": message})
                response = await CommonHttps.make_request(url=url, method=request_method, headers=headers, body=message,
                                                          client_cert=self._client_cert, client_key=self._client_key,
                                                          ca_certs=self._ca_certs)
                logger.info("0002", "Sent message: {message}, with {headers} to {url} and received status code {code}",
                            {"headers": headers, "url": url, "message": message, "code": response.code})
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
                    logger.warning("0004",
                                   "A request has exceeded the maximum number of retries, {max_retries} retries",
                                   {"max_retries": self._max_retries})
                    raise MaxRetriesExceeded("The max number of retries to make a request has been exceeded") from e

    def _is_tornado_network_error(self, e):
        if isinstance(e, httpclient.HTTPClientError):
            if e.code == 599:
                return True

        return False

    def _is_retriable(self, e):
        if self._is_tornado_network_error(e):
            return True

        for error_type in self.errors_not_to_retry:
            if isinstance(e, error_type):
                return False

        return True
