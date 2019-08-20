"""This module defines the outbound transmission component."""

from pathlib import Path

from comms import transmission_adaptor
from tornado import httpclient
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger("OUTBOUND_TRANSMISSION")


class MaxRetriesExceeded(Exception):
    pass


class OutboundTransmission(transmission_adaptor.TransmissionAdaptor):
    errors_not_to_retry = [
        httpclient.HTTPClientError
    ]

    """A component that sends HTTP requests to a remote MHS."""

    def __init__(self, certs_dir, client_cert, client_key, ca_certs, max_retries):
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

    async def make_request(self, interaction_details, message) -> httpclient.HTTPResponse:
        """Make a request for the specified interaction, containing the provided message. Raises an exception if a
        non-success HTTP status code is returned by the server.

        :param interaction_details: A dictionary containing details of the interaction this message is for.
        :param message: The message body to send.
        :return: The tornado HTTPResponse object that represents the reponse of the object
        """

        url = interaction_details['url']

        headers = OutboundTransmission._build_headers(interaction_details)

        request_method = OutboundTransmission._get_request_method(interaction_details)

        logger.info("001", "About to send message with {headers} to {url} : {message}",
                    {"headers": headers, "url": url, "message": message})

        retries_remaining = self._max_retries
        while retries_remaining > 0:
            try:
                response = await httpclient.AsyncHTTPClient().fetch(url,
                                                                    method=request_method,
                                                                    body=message,
                                                                    headers=headers,
                                                                    client_cert=self._client_cert,
                                                                    client_key=self._client_key,
                                                                    ca_certs=self._ca_certs)
                return response
            except Exception as e:
                if self._is_retriable(e):
                    retries_remaining -= 1
                    logger.warning("002",
                                   "A retriable error was encountered {exception} {retries_remaining} {max_retries}",
                                   {"exception": e,
                                    "retries_remaining": retries_remaining,
                                    "max_retries": self._max_retries
                                    })
                else:
                    raise e

        raise MaxRetriesExceeded("The max number of retries to make a request has been exceeded")

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

    @staticmethod
    def _build_headers(interaction_details):
        headers = {'type': interaction_details['type'],
                   'Content-Type': interaction_details['content_type'],
                   'charset': interaction_details['charset'],
                   'SOAPAction': interaction_details['soap_action'],
                   'start': interaction_details['start']}
        return headers

    @staticmethod
    def _get_request_method(interaction_details):
        request_method = "POST"

        if interaction_details['request_type'] == "GET":
            request_method = "GET"

        return request_method
