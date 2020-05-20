"""Component tests related to the asynchronous-express message pattern"""

import unittest

from integration_tests.assertors.json_error_response_assertor import JsonErrorResponseAssertor
from integration_tests.db.db_wrapper_factory import MHS_STATE_TABLE_WRAPPER, MHS_SYNC_ASYNC_TABLE_WRAPPER
from integration_tests.db.mhs_table import MhsTableStateAssertor
from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder


class AsynchronousExpressMssagingPatternTests(unittest.TestCase):
    """
    These tests show an asynchronous express response from Spine via the MHS for the example message interaction
    of PSIS(Personal Spine Information Service).

    They make use of the fake-spine service, which has known responses for certain message ids.
    They make use of the fake-spine-route-lookup service, which has known responses for certain interaction ids.
    """

    def setUp(self):
        MHS_STATE_TABLE_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_WRAPPER.clear_all_records_in_table()

    def test_should_return_information_from_soap_fault_returned_from_spine_in_original_post_request_to_client(self):
        """
        Message ID: AD7D39A8-1B6C-4520-8367-6B7BEBD7B842 configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923',
                                            message_id='AD7D39A8-1B6C-4520-8367-6B7BEBD7B842'
                                            )
        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
            .assert_error_code(200) \
            .assert_code_context('urn:nhs:names:error:tms') \
            .assert_severity('Error')

    def test_should_record_message_status_as_nackd_when_soap_error_response_returned_from_spine(self):
        """
        Message ID: AD7D39A8-1B6C-4520-8367-6B7BEBD7B842 configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923',
                                            message_id='AD7D39A8-1B6C-4520-8367-6B7BEBD7B842'
                                            )

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_NACKD',
                'WORKFLOW': 'async-express'
            })

    def test_should_return_information_from_ebxml_fault_returned_from_spine_in_original_post_request(self):
        """
        Message ID: '7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA' configured in fakespine to return a ebxml Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/ebxml_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923',
                                            message_id='7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA'
                                            )
        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
            .assert_code_context('urn:oasis:names:tc:ebxml-msg:service:errors') \
            .assert_severity('Error') \
            .assert_error_type('ebxml_error')

    def test_should_record_message_status_as_nackd_when_ebxml_error_response_returned_from_spine(self):
        """
        Message ID: '7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA' configured in fakespine to return a ebxml Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/ebxml_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923',
                                            message_id='7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA'
                                            )
        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_NACKD',
                'WORKFLOW': 'async-express'
            })

    def test_should_return_information_from_soap_fault_returned_from_spine_in_original_request_to_client_when_wait_for_response_requested(self):
        """
        Message ID: AD7D39A8-1B6C-4520-8367-6B7BEBD7B842 configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923',
                                            message_id='AD7D39A8-1B6C-4520-8367-6B7BEBD7B842'
                                            )
        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=True) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
            .assert_error_code(200) \
            .assert_code_context('urn:nhs:names:error:tms') \
            .assert_severity('Error')

    def test_should_record_message_status_when_soap_error_response_returned_from_spine_and_wait_for_response_requested(self):
        """
        Message ID: AD7D39A8-1B6C-4520-8367-6B7BEBD7B842 configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923',
                                            message_id='AD7D39A8-1B6C-4520-8367-6B7BEBD7B842'
                                            )
        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=True) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED',
                'WORKFLOW': 'sync-async'
            })

    def test_should_return_information_in_ebxml_fault_returned_from_spine_in_original_post_request_to_client_when_wait_for_response_requested(self):
        """
        Message ID: '7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA' configured in fakespine to return a ebxml Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/ebxml_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923',
                                            message_id='7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA'
                                            )
        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=True) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
            .assert_code_context('urn:oasis:names:tc:ebxml-msg:service:errors') \
            .assert_severity('Error') \
            .assert_error_type('ebxml_error')

    def test_should_record_message_status_when_ebxml_error_response_returned_from_spine_and_wait_for_response_requested(self):
        """
        Message ID: '7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA' configured in fakespine to return a ebxml Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/ebxml_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923',
                                            message_id='7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA'
                                            )
        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=True) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED',
                'WORKFLOW': 'sync-async'
            })

    def test_should_return_bad_request_when_client_sends_invalid_message(self):
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689174606')

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, wait_for_response=False) \
            .with_body({'blah': '123'}) \
            .execute_post_expecting_bad_request_response()

        # Assert
        self.assertEqual(response.text, "400: Invalid request. Validation errors: {'payload': ['Not a valid string.']}")
