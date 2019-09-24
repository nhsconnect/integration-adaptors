"""
Provides tests around the Asynchronous Reliable workflow, including sync-async wrapping
"""
from unittest import TestCase

from integration_tests.amq.amq import MHS_INBOUND_QUEUE
from integration_tests.amq.amq_message_assertor import AMQMessageAssertor
from integration_tests.assertors.assert_with_retries import AssertWithRetries
from integration_tests.dynamo.dynamo import MHS_STATE_TABLE_DYNAMO_WRAPPER, MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.dynamo.dynamo_sync_async_mhs_table import DynamoSyncAsyncMhsTableStateAssertor
from integration_tests.helpers.build_message import build_message
from integration_tests.helpers.methods import get_asid
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder
from integration_tests.xml.hl7_xml_assertor import Hl7XmlResponseAssertor


class AsynchronousReliableMessagingPatternTests(TestCase):
    """
     These tests show an asynchronous reliable response from Spine via the MHS for the example message interaction of
     GP Summary.

    Asynchronous message interaction:
    - Message sent: GP Summary (REPC_IN150016UK05)
    - Expected response: Application Acknowledgement (MCCI_IN010000UK13)

    Flow documented at:
    - https://data.developer.nhs.uk/dms/mim/6.3.01/Index.htm
        -> Domains - Health and Clinical Management
            -> GP Summary
                -> 7.2 (Request)
            -> Infrastructure
                -> 4.2 (Response)
    """

    def setUp(self):
        MHS_STATE_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()

    def test_should_return_successful_response_from_spine_to_message_queue(self):
        # Arrange
        message, message_id = build_message('REPC_IN150016UK05', get_asid(), '9446245796', 'Asynchronous Reliable test')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='REPC_IN150016UK05',
                          message_id=message_id,
                          sync_async=False,
                          correlation_id='1') \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue()) \
            .assert_property('message-id', message_id) \
            .assert_property('correlation-id', '1') \
            .assertor_for_hl7_xml_message() \
            .assert_element_exists_with_value('.//requestSuccessDetail//detail', 'GP Summary upload successful')

    def test_should_record_asynchronous_reliable_message_status_as_successful(self):
        # Arrange
        message, message_id = build_message('REPC_IN150016UK05', get_asid(), '9446245796', 'Asynchronous Express test')

        print(message)
        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='REPC_IN150016UK05',
                          message_id=message_id,
                          sync_async=False,
                          correlation_id='1') \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue()) \
            .assertor_for_hl7_xml_message() \
            .assert_element_exists_with_value('.//requestSuccessDetail//detail', 'GP Summary upload successful')

        AssertWithRetries(retry_count=10) \
            .assert_condition_met(lambda: DynamoMhsTableStateAssertor.wait_for_inbound_response_processed(message_id))

        DynamoMhsTableStateAssertor(MHS_STATE_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values({
            'INBOUND_STATUS': 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED',
            'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_ACKD',
            'WORKFLOW': 'async-reliable'
        })

    def test_should_return_successful_response_from_spine_in_original_post_request_body_if_sync_async_requested(self):
        # Arrange
        message, message_id = build_message('REPC_IN150016UK05', get_asid(), '9446245796', 'Asynchronous Reliable test')

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='REPC_IN150016UK05', message_id=message_id, sync_async=True) \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        Hl7XmlResponseAssertor(response.text) \
            .assert_element_exists_with_value('.//requestSuccessDetail//detail', 'GP Summary upload successful')

    def test_should_record_the_correct_response_between_the_inbound_and_outbound_components_if_sync_async_requested(self):
        # Arrange
        message, message_id = build_message('REPC_IN150016UK05', get_asid(), '9446245796', 'Asynchronous Reliable test')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='REPC_IN150016UK05',
                          message_id=message_id,
                          sync_async=True,
                          correlation_id='1') \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        DynamoSyncAsyncMhsTableStateAssertor(MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_element_exists_with_value('.//requestSuccessDetail//detail', 'GP Summary upload successful')
