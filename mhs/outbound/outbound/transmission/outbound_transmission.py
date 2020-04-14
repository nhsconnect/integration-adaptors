"""This module defines the outbound transmission component."""

from ssl import SSLError
from typing import Dict

from comms.common_https import CommonHttps
from retry import retriable_action
from mhs_common.transmission import transmission_adaptor
from tornado import httpclient
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


class OutboundTransmissionError(Exception):
    pass


class OutboundTransmission(transmission_adaptor.TransmissionAdaptor):
    errors_not_to_retry = (
        httpclient.HTTPClientError,
        SSLError
    )

    """A component that sends HTTP requests to a remote MHS."""

    def __init__(self, client_cert: str, client_key: str, ca_certs: str, max_retries: int,
                 retry_delay: int, validate_cert: bool, http_proxy_host: str = None, http_proxy_port: int = None):
        """Create a new OutboundTransmission that loads certificates from the specified directory.

        :param client_cert: A string containing the filepath of the client certificate file.
        :param client_key: A string containing the filepath of the client private key file.
        :param ca_certs: A string containing the filepath of the certificate authority certificate file.
        :param max_retries: An integer with the value of the max number times to retry sending the request if it fails.
        :param retry_delay: An integer representing the delay (in milliseconds) to use between retry attempts.
        :param http_proxy_host The hostname of the HTTP proxy to be used.
        :param http_proxy_port The port of the HTTP proxy to be used.
        """
        self._client_cert = client_cert
        self._client_key = client_key
        self._ca_certs = ca_certs
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._validate_cert = validate_cert

        self._proxy_host = http_proxy_host
        self._proxy_port = http_proxy_port

    async def make_request(self, url: str, headers: Dict[str, str], message: str,
                           raise_error_response: bool = True) -> httpclient.HTTPResponse:

        async def make_http_request():
            logger.info("About to send message with {headers} to {url} using {proxy_host} & {proxy_port}",
                        fparams={
                            "headers": headers,
                            "url": url,
                            "proxy_host": self._proxy_host,
                            "proxy_port": self._proxy_port
                        })
            response = await CommonHttps.make_request(url=url, method="POST", headers=headers, body=message,
                                                      client_cert=self._client_cert, client_key=self._client_key,
                                                      ca_certs=self._ca_certs, validate_cert=self._validate_cert,
                                                      http_proxy_host=self._proxy_host,
                                                      http_proxy_port=self._proxy_port,
                                                      raise_error_response=raise_error_response)
            logger.info("Sent message with {headers} to {url} using {proxy_host} & {proxy_port} and "
                        "received status code {code}",
                        fparams={
                            "headers": headers,
                            "url": url,
                            "proxy_host": self._proxy_host,
                            "proxy_port": self._proxy_port,
                            "code": response.code
                        })
            return response

        retry_result = await retriable_action.RetriableAction(make_http_request, self._max_retries,
                                                              self._retry_delay / 1000) \
            .with_success_check(lambda r: r.code != 599) \
            .with_retriable_exception_check(self._is_exception_retriable) \
            .execute()

        if not retry_result.is_successful:
            logger.error("Failed to make outbound HTTP request to {url}", fparams={"url": url})

            exception_raised = retry_result.exception
            if exception_raised:
                raise exception_raised
            else:
                raise OutboundTransmissionError("The max number of retries to make a request has been exceeded")

        return retry_result.result

    def _is_tornado_network_error(self, e: Exception) -> bool:
        return isinstance(e, httpclient.HTTPClientError) and e.code == 599

    def _is_exception_retriable(self, e: Exception) -> bool:
        retriable = True

        if isinstance(e, self.errors_not_to_retry):
            retriable = False

        # While we normally don't want to retry on an HTTP error, there is a special case where the Tornado
        # HTTPClientError's code is set to 599, which actually represents a connection error, rather than an HTTP error
        # response.
        if self._is_tornado_network_error(e):
            retriable = True

        return retriable
