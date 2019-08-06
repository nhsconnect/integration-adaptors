"""This module defines the outbound transmission component."""

import logging
from pathlib import Path

import requests


class OutboundTransmission:
    """A component that sends HTTP requests to a remote MHS."""

    def __init__(self, certs_dir):
        """Create a new OutboundTransmission that loads certificates from the specified directory.
        :param certs_dir: A string containing the path to the directory to load certificates from.
        """
        client_cert_path = str(Path(certs_dir) / "client.cert")
        client_key_path = str(Path(certs_dir) / "client.key")
        self._cert = (client_cert_path, client_key_path)
        self._verify = str(Path(certs_dir) / "client.pem")

    def make_request(self, interaction_details, message):
        """Make a request for the specified interaction, containing the provided message. Raises an exception if a
        non-success HTTP status code is returned by the server.

        :param interaction_details: A dictionary containing details of the interaction this message is for.
        :param message: The message body to send.
        :return: The content of the response returned by the remote end.
        """

        url = interaction_details['url']

        headers = OutboundTransmission._build_headers(interaction_details)

        request_method = OutboundTransmission._get_request_method(interaction_details)

        logging.debug("About to send message with headers '%s' to URL '%s': %s", headers, url, message)

        response = request_method(url,
                                  data=message,
                                  headers=headers,
                                  cert=self._cert,
                                  verify=self._verify)

        # Raise an error if a 4xx or 5xx HTTP status was returned.
        response.raise_for_status()

        return response.content

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
        request_method = requests.post

        if interaction_details['request_type'] == "GET":
            request_method = requests.get

        return request_method
