"""
Provides tests around the Synchronous workflow
"""
import unittest
import re
from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder


class TextErrorResponseAssertor(object):

    def __init__(self, received_message: str):
        self.received_message = received_message
        self.assertor = unittest.TestCase('__init__')

    def assert_error_code(self, expected_error_code: int):
        expression = re.compile('(errorCode=(?P<errorCode>[0-9]+))')
        matches = expression.search(self.received_message)
        if len(matches.groups()) != 2:
            raise Exception("No error code found in the returned string")

        matching_groups = matches.group('errorCode')
        self.assertor.assertEqual(int(matching_groups), expected_error_code, 'Error code did not match expected value')

        return self


class SynchronousMessagingPatternTests(unittest.TestCase):
    """
     These tests show a synchronous response from Spine via the MHS for the example message interaction of PDS
    (Personal Demographics Service).

    They make use of the fake-spine service, which has known responses for certain message ids.
    They make use of the fake-spine-route-lookup service, which has known responses for certain interaction ids.
    """

    def test_should_return_error_response_to_client_when_error_response_returned_from_spine(self):
        # Arrange
        message, message_id = build_message('QUPA_IN040000UK32', '9689174606')

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPA_IN040000UK32', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert

        TextErrorResponseAssertor(response.text)\
            .assert_error_code(200)
