"""
Provides assertions over the json response format we get from the MHS when an error is returned from Spine
"""
from __future__ import annotations

import json
import unittest


class JsonErrorResponseAssertor(object):
    """
    Provides assertions over the json response format we get from the MHS when an error is returned from Spine
    """

    def __init__(self, received_message: str):
        self.received_message = json.loads(received_message)
        self.assertor = unittest.TestCase('__init__')

    def assert_error_code(self, expected_error_code: int) -> JsonErrorResponseAssertor:
        self.assertor.assertEqual(self.received_message['errors'][0]['errorCode'], str(expected_error_code),
                                  'Error code did not match expected value')
        return self

    def assert_code_context(self, expected_code_context: str) -> JsonErrorResponseAssertor:
        self.assertor.assertEqual(self.received_message['errors'][0]['codeContext'], expected_code_context,
                                  'Code context did not match expected value')
        return self

    def assert_severity(self, expected_severity: str) -> JsonErrorResponseAssertor:
        self.assertor.assertEqual(self.received_message['errors'][0]['severity'], expected_severity,
                                  'Severity did not match expected value')
        return self

    def assert_error_type(self, expected_error_type) -> JsonErrorResponseAssertor:
        self.assertor.assertEqual(self.received_message['errors'][0]['errorType'], expected_error_type,
                                  'errorType did not match expected value')
        return self
