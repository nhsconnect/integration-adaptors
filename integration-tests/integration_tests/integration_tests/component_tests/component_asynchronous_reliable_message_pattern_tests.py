"""Component tests related to the asynchronous-reliable message pattern"""

import unittest

from integration_tests.dynamo.dynamo import MHS_STATE_TABLE_DYNAMO_WRAPPER, MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder


class SynchronousMessagingPatternTests(unittest.TestCase):
    """
    These tests show an asynchronous reliable response from Spine via the MHS for the example message interaction
    of GP Summary Upload (REPC_IN150016UK05)

    They make use of the fake-spine service, which has known responses for certain message ids.
    They make use of the fake-spine-route-lookup service, which has known responses for certain interaction ids.
    """

    def setUp(self):
        MHS_STATE_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()

    def test_should_return_success_response_to_the_client_when_a_business_level_retry_is_required_and_succeeds(self):
        """
        Message ID: '35586865-45B0-41A5-98F6-817CA6F1F5EF' configured in fakespine to return a SOAP Fault error,
        after 2 retries fakespine will return a success response.
        """

        # Arrange
        message, message_id = build_message('REPC_IN150016UK05', '9689177923',
                                            message_id='35586865-45B0-41A5-98F6-817CA6F1F5EF'
                                            )
        # Act: Response should be 202
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='REPC_IN150016UK05 ', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_success()

    def test_should_record_message_status_when_a_business_level_retry_is_required_and_succeeds(self):
        """
        Message ID: '35586865-45B0-41A5-98F6-817CA6F1F5EF' configured in fakespine to return a SOAP Fault error,
        after 2 retries fakespine will return a success response.
        """

        # Arrange
        message, message_id = build_message('REPC_IN150016UK05', '9689177923',
                                            message_id='35586865-45B0-41A5-98F6-817CA6F1F5EF'
                                            )
        # Act: Response should be 202
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='REPC_IN150016UK05 ', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        DynamoMhsTableStateAssertor(MHS_STATE_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_ACKD',
                'WORKFLOW': 'async-reliable'
            })
