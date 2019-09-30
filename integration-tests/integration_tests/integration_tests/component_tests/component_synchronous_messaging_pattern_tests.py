"""
Provides tests around the Synchronous workflow
"""
from unittest import TestCase

from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder
from integration_tests.xml.hl7_xml_assertor import Hl7XmlResponseAssertor


class SynchronousMessagingPatternTests(TestCase):
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
        # Hl7XmlResponseAssertor(response.text) \
        #     .assert_element_exists('.//retrievalQueryResponse//QUPA_IN050000UK32//PdsSuccessfulRetrieval')
