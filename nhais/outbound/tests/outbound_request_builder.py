from __future__ import annotations

import json
import unittest
import uuid

import requests
from fhir.resources.patient import Patient
from requests import Response

from comms.http_headers import HttpHeaders
from utilities import config


class OutboundRequestBuilder(object):
    """
    Responsible for building HTTP requests against the NHAIS service.
    """

    def __init__(self):
        self.headers = {}
        self.body = None
        self.request_url = config.get_config('OUTBOUND_ADDRESS', 'http://localhost') + "/"
        self.assertor = unittest.TestCase('__init__')

    def with_headers(self, correlation_id: str = str(uuid.uuid4()).upper()) -> OutboundRequestBuilder:
        """
        Allows the setting of required headers
        :param correlation_id: the correlation id used
        :return: self
        """
        self.headers = {
            HttpHeaders.CORRELATION_ID: correlation_id,
            HttpHeaders.CONTENT_TYPE: 'application/json',
        }

        return self

    def with_acceptance_patient(self, patient: Patient) -> OutboundRequestBuilder:
        """
        Allows the setting of the payload for the HTTP request
        :param patient: the payload to send
        :return: self
        """
        self.request_url += f'fhir/Patient/{patient.id}'
        self.body = json.dumps(patient.as_json())
        return self

    def execute_post_expecting_success(self) -> Response:
        """
        Execute a POST request against the configured body and headers within this class.
        Asserts the response is successful.
        :return: response
        """
        response = self._execute_post_request()
        self.assertor.assertTrue(
            response.ok,
            f'A non successful error code was returned from server: {response.status_code} {response.text}')

        return response

    def execute_post_expecting_error_response(self) -> Response:
        """
        Execute a POST request against the configured body and headers within this class.
        Asserts the response is 500.
        :return: response
        """
        response = self._execute_post_request()
        self.assertor.assertTrue(
            response.status_code == 500,
            f'A non 500 error code was returned from server: {response.status_code} {response.text}')

        return response

    def execute_post_expecting_bad_request_response(self) -> Response:
        """
        Execute a POST request against the configured body and headers within this class.
        Asserts the response is 400.
        :return: response
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
        return requests.post(self.request_url, headers=self.headers, data=self.body, verify=False, timeout=15)
