"""Component tests related to the asynchronous-express message pattern"""

import unittest

from integration_tests.assertors.text_error_response_assertor import TextErrorResponseAssertor
from integration_tests.dynamo.dynamo import MHS_STATE_TABLE_DYNAMO_WRAPPER, MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder


class SynchronousMessagingPatternTests(unittest.TestCase):
    """
         These tests show an asynchronous express response from Spine via the MHS for the example message interaction
          of PSIS(Personal Spine Information Service).

    They make use of the fake-spine service, which has known responses for certain message ids.
    They make use of the fake-spine-route-lookup service, which has known responses for certain interaction ids.
    """

    def setUp(self):
        MHS_STATE_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()

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
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        TextErrorResponseAssertor(response.text) \
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
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        DynamoMhsTableStateAssertor(MHS_STATE_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_NACKD',
                'WORKFLOW': 'async-express'
            })
