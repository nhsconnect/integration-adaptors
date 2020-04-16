"""Module responsible for building and sending http messages to the SCR Adaptor"""
from __future__ import annotations

import os
import unittest
import uuid

import requests
from requests import Response

from comms.http_headers import HttpHeaders


class ScrHttpRequestBuilder(object):
    """
    Responsible for building HTTP requests to the SCR service
    """

    def __init__(self):
        self.headers = {}
        self.body = None
        self.scr_host = os.environ.get('SCR_ADDRESS')
        self.assertor = unittest.TestCase('__init__')

    def with_headers(self, interaction_name: str, message_id: str,
                     correlation_id: str = str(uuid.uuid4()).upper()) -> ScrHttpRequestBuilder:
        """
        Sets the required headers for the SCR Adaptor
        :param correlation_id: the correlation id used
        :param interaction_name: id of this interaction used within MHS to track this request lifecycle
        :param message_id: the message id
        :return: self
        """
        self.headers = {
            'Interaction-name': interaction_name,
            HttpHeaders.MESSAGE_ID: message_id,
            HttpHeaders.CORRELATION_ID: correlation_id
        }

        return self

    def with_body(self, body) -> ScrHttpRequestBuilder:
        """
        Sets the payload of the HTTP request
        :param body: the payload to send
        :return: self
        """
        self.body = body

        return self
    
    def execute_post_expecting_success(self) -> Response:
        """
        Execute a POST request against the SCR adaptor using the configured body and headers within this class.
        Asserts the response is successful.
        :return: Response
        """
        response = requests.post(self.scr_host, headers=self.headers, data=self.body)
        self.assertor.assertTrue(
            response.ok,
            f'A non successful error code was returned from server: {response.status_code} {response.text}')

        return response

    def execute_post_expecting_bad_request_response(self) -> Response:
        """
        Executes a POST request against the SCR Adaptor, asserts the response status code is 400 
        :return: Response
        """
        response = requests.post(self.scr_host, headers=self.headers, data=self.body)
        self.assertor.assertTrue(
            response.status_code == 400,
            f'A non 400 error code was returned from server: {response.status_code} {response.text}')
        return response
    
    def execute_post_expecting_internal_server_error(self) -> Response:
        """
        Executes a POST request against the SCR Adaptor, asserts the response status code is 500 
        :return: Response
        """
        response = requests.post(self.scr_host, headers=self.headers, data=self.body)
        self.assertor.assertTrue(
            response.status_code == 500,
            f'A non 400 error code was returned from server: {response.status_code} {response.text}')
        return response
