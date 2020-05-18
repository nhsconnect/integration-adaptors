"""
Provides functionality for calling the MHS over HTTP
"""
from __future__ import annotations

import json
import os
import unittest
import uuid
from typing import Optional

import requests

from comms.http_headers import HttpHeaders
from integration_tests.helpers.asid_provider import get_asid
from requests import Response


class MhsHttpRequestBuilder(object):
    """
    Responsible for building HTTP requests against the MHS service.
    """

    def __init__(self):
        self.headers = {}
        self.body = None
        self.mhs_host = os.environ.get('MHS_ADDRESS', 'http://localhost') + "/"
        self.assertor = unittest.TestCase('__init__')

    def with_headers(self, interaction_id: str,
                     message_id: str,
                     wait_for_response: bool,
                     correlation_id: str = str(uuid.uuid4()).upper(),
                     ods_code: str = "YES",
                     from_asid: Optional[str] = f'{get_asid()}') -> MhsHttpRequestBuilder:
        """
        Allows the setting of required headers for the MHS
        :param from_asid: the identifier of the calling system
        :param ods_code: the ods code of the system you wish to communicate with (spine is YES)
        :param correlation_id: the correlation id used
        :param interaction_id: id of this interaction used within MHS to track this request lifecycle
        :param message_id: the message id
        :param wait_for_response: whether this request should execute synchronously or not
        :return: self
        """
        self.headers = {
            HttpHeaders.INTERACTION_ID: interaction_id,
            HttpHeaders.MESSAGE_ID: message_id,
            HttpHeaders.CORRELATION_ID: correlation_id,
            HttpHeaders.WAIT_FOR_RESPONSE: str(wait_for_response).lower(),
            HttpHeaders.FROM_ASID: from_asid,
            HttpHeaders.CONTENT_TYPE: 'application/json',
            HttpHeaders.ODS_CODE: ods_code
        }

        return self

    def with_body(self, body, attachments=None) -> MhsHttpRequestBuilder:
        """
        Allows the setting of the payload for the HTTP request
        :param body: the payload to send
        :param attachments: any attachments to send
        :return: self
        """
        if attachments:
            self.body = json.dumps({"payload": body,
                                    "attachments": attachments})
        else:
            self.body = json.dumps({"payload": body})

        return self

    def execute_post_expecting_success(self) -> Response:
        """
        Execute a POST request against the MHS using the configured body and headers within this class.
        Asserts the response is successful.
        :return: response from MHS
        """
        response = self._execute_post_request()
        self.assertor.assertTrue(
            response.ok,
            f'A non successful error code was returned from server: {response.status_code} {response.text}')

        return response

    def execute_post_expecting_error_response(self) -> Response:
        """
        Execute a POST request against the MHS using the configured body and headers within this class.
        Asserts the response is 500.
        :return: response from MHS
        """
        response = self._execute_post_request()
        self.assertor.assertTrue(
            response.status_code == 500,
            f'A non 500 error code was returned from server: {response.status_code} {response.text}')

        return response

    def execute_post_expecting_bad_request_response(self) -> Response:
        """
        Execute a POST request against the MHS using the configured body and headers within this class.
        Asserts the response is 400.
        :return: response from MHS
        """
        response = self._execute_post_request()
        self.assertor.assertTrue(
            response.status_code == 400,
            f'A non 400 error code was returned from server: {response.status_code} {response.text}')

        return response

    def _execute_post_request(self) -> Response:
        """
        Execute a POST request against the MHS using the configured body and headers within this class.
        :return: response from MHS
        """
        return requests.post(self.mhs_host, headers=self.headers, data=self.body, verify=False, timeout=15)
