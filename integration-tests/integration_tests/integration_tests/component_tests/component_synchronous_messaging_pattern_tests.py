"""
Provides tests around the Synchronous workflow
"""
import unittest

from integration_tests.assertors.json_error_response_assertor import JsonErrorResponseAssertor
from integration_tests.db.db_wrapper_factory import MHS_STATE_TABLE_WRAPPER, MHS_SYNC_ASYNC_TABLE_WRAPPER
from integration_tests.db.mhs_table import MhsTableStateAssertor
from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder


class SynchronousMessagingPatternTests(unittest.TestCase):
    """
     These tests show a synchronous response from Spine via the MHS for the example message interaction of PDS
    (Personal Demographics Service).

    They make use of the fake-spine service, which has known responses for certain message ids.
    They make use of the fake-spine-route-lookup service, which has known responses for certain interaction ids.
    """

    def setUp(self):
        MHS_STATE_TABLE_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_WRAPPER.clear_all_records_in_table()

    def test_should_return_error_response_to_client_when_error_response_returned_from_spine(self):
        """
        Message ID: F5187FB6-B033-4A75-838B-9E7A1AFB3111 configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPA_IN040000UK32', '9689174606', message_id='F5187FB6-B033-4A75-838B-9E7A1AFB3111')

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPA_IN040000UK32', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
            .assert_error_code(200) \
            .assert_code_context('urn:nhs:names:error:tms') \
            .assert_severity('Error') \
            .assert_error_type('soap_fault')

    def test_should_record_message_status_as_successful_when_error_response_returned_from_spine(self):
        """
        Message ID: F5187FB6-B033-4A75-838B-9E7A1AFB3111 configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPA_IN040000UK32', '9689174606',
                                            message_id='F5187FB6-B033-4A75-838B-9E7A1AFB3111')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPA_IN040000UK32', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'SYNC_RESPONSE_SUCCESSFUL',
                'WORKFLOW': 'sync'
            })

    def test_should_return_bad_request_when_client_sends_invalid_message(self):
        # Arrange
        message, message_id = build_message('QUPA_IN040000UK32', '9689174606')

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPA_IN040000UK32', message_id=message_id, wait_for_response=False, from_asid=None) \
            .with_body(message) \
            .execute_post_expecting_bad_request_response()

        # Assert
        self.assertEqual(response.text, "`from_asid` header field required for sync messages")

    def test_should_record_message_received_when_bad_request_returned_to_client(self):
        # Arrange
        message, message_id = build_message('QUPA_IN040000UK32', '9689174606')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPA_IN040000UK32', message_id=message_id, wait_for_response=False, from_asid=None) \
            .with_body(message) \
            .execute_post_expecting_bad_request_response()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values({
            'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_RECEIVED',
            'WORKFLOW': 'sync'
        })
