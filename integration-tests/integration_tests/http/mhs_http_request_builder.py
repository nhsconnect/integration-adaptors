"""
Provides functionality for calling the MHS over HTTP
"""
from __future__ import annotations

import os
import unittest
import uuid

import requests
from requests import Response

from integration_tests.helpers.methods import get_asid


class MhsHttpRequestBuilder(object):
    """
    Responsible for building HTTP requests against the MHS service.
    """

    def __init__(self):
        self.headers = {}
        self.body = None
        self.mhs_host = "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"
        self.assertor = unittest.TestCase('__init__')

    def with_headers(self, interaction_id: str, message_id: str, sync_async: bool, correlation_id: str = str(uuid.uuid4()).upper(), ods_code: str = "YES") -> MhsHttpRequestBuilder:
        """
        Allows the setting of required headers for the MHS
        :param ods_code: the ods code of the system you wish to communicate with (spine is YES)
        :param correlation_id: the correlation id used
        :param interaction_id: id of this interaction used within MHS to track this request lifecycle
        :param message_id: the message id
        :param sync_async: whether this request should execute synchronously or not
        :return: self
        """
        self.headers = {
            'Interaction-Id': interaction_id,
            'Message-Id': message_id,
            'Correlation-Id': correlation_id,
            'sync-async': str(sync_async).lower(),
            'from-asid': f'{get_asid()}',
            'ods-code': ods_code
        }

        return self

    def with_body(self, body) -> MhsHttpRequestBuilder:
        """
        Allows the setting of the payload for the HTTP request
        :param body: the payload to send
        :return: self
        """
        self.body = body

        return self

    def execute_post_expecting_success(self) -> Response:
        """
        Execute a POST request against the MHS using the configured body and headers within this class.
        Asserts the response is successful.
        :return: self
        """
        response = requests.post(self.mhs_host, headers=self.headers, data=self.body)
        self.assertor.assertTrue(
            response.ok,
            f'A non successful error code was returned from server: {response.status_code}')

        return response
