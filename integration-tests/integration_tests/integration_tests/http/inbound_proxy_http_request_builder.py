"""
Provides functionality for calling the inbound service of the MHS, via a proxy, over HTTP
"""
from __future__ import annotations
import os
import unittest
import requests
from requests import Response
from comms.http_headers import HttpHeaders


class InboundProxyHttpRequestBuilder(object):
    """
    Responsible for building HTTP requests against the MHS service.
    """

    def __init__(self):
        self.headers = {
            HttpHeaders.CONTENT_TYPE: 'multipart/related; boundary="--=_MIME-Boundary"'
        }
        self.body = None
        self.inbound_proxy_host = os.environ.get('INBOUND_PROXY_HOST', 'http://fakespine:8888') + "/inbound-proxy"
        self.assertor = unittest.TestCase('__init__')

    def with_body(self, body) -> InboundProxyHttpRequestBuilder:
        """
        Allows the setting of the payload for the HTTP request
        :param body: the payload to send
        :return: self
        """
        self.body = body

        return self

    def execute_post_expecting_success(self) -> Response:
        """
        Execute a POST request against the INBOUND_PROXY using the configured body and headers within this class.
        Asserts the response is successful.
        :return: response from MHS inbound service
        """
        response = self._execute_post_request()
        self.assertor.assertTrue(
            response.ok,
            f'A non successful error code was returned from server: {response.status_code} {response.text}')

        return response

    def execute_post_expecting_error_response(self) -> Response:
        """
        Execute a POST request against the INBOUND_PROXY using the configured body and headers within this class.
        Asserts the response is 500.
        :return: response from MHS inbound service
        """
        response = self._execute_post_request()
        self.assertor.assertTrue(
            response.status_code == 500,
            f'A non 500 error code was returned from server: {response.status_code} {response.text}')

        return response

    def _execute_post_request(self) -> Response:
        """
        Execute a POST request against the INBOUND_PROXY using the configured body and headers within this class.
        :return: response from MHS inbound service
        """
        return requests.post(self.inbound_proxy_host, headers=self.headers, data=self.body, verify=False)
