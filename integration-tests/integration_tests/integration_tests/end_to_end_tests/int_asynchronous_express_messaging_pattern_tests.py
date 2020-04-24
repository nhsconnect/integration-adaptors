"""
Provides tests around the Asynchronous Express workflow, including sync-async wrapping
"""
import json
from unittest import TestCase

from integration_tests.amq.amq import MHS_INBOUND_QUEUE
from integration_tests.amq.amq_message_assertor import AMQMessageAssertor
from integration_tests.assertors.assert_with_retries import AssertWithRetries
from integration_tests.dynamo.dynamo import MHS_STATE_TABLE_DYNAMO_WRAPPER, MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.dynamo.dynamo_sync_async_mhs_table import DynamoSyncAsyncMhsTableStateAssertor
from integration_tests.end_to_end_tests.common_assertions import CommonAssertions
from integration_tests.helpers.concurrent_requests import send_messages_concurrently, \
    assert_all_messages_succeeded, has_errors
from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder


class AsynchronousExpressMessagingPatternTests(TestCase):
    """
     These tests show an asynchronous express response from Spine via the MHS for the example message interaction of PSIS
    (Personal Spine Information Service).

    Asynchronous message interaction:
    - Message sent: PSIS Document List Data Request (QUPC_IN160101UK05)
    - Expected response: PSIS Document List Data Retrieval (QUPC_IN160102UK05)

    Flow documented at:
    - https://data.developer.nhs.uk/dms/mim/6.3.01/Index.htm
        -> Domains - Health and Clinical Management
            -> PSIS Query
                -> 6.1 (Request)
                -> 6.2 (Response)
    """

    def setUp(self):
        MHS_STATE_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()
        MHS_INBOUND_QUEUE.drain()
        self.assertions = CommonAssertions('async-express')

    def test_should_return_successful_response_from_spine_to_message_queue(self):
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', '9689177923')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05',
                          message_id=message_id,
                          sync_async=False,
                          correlation_id='1') \
            .with_body(message) \
            .execute_post_expecting_success()

        AssertWithRetries(retry_count=10) \
            .assert_condition_met(lambda: DynamoMhsTableStateAssertor.wait_for_inbound_response_processed(message_id))

        amq_assertor = AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue())
        state_table_assertor = DynamoMhsTableStateAssertor(MHS_STATE_TABLE_DYNAMO_WRAPPER.get_all_records_in_table())

        self.assertions.spline_reply_published_to_message_queue(amq_assertor, message_id)
        hl7_xml_message_assertor = amq_assertor.assertor_for_hl7_xml_message()
        self.assertions.hl7_xml_contains_response_code_and_patient_id(hl7_xml_message_assertor)
        self.assertions.message_status_recorded_as_successfully_processed(state_table_assertor, message_id)

    def test_should_return_successful_response_and_record_spine_reply_in_resync_table_if_sync_async_requested(self):
        # Arrange
        messages = [build_message('QUPC_IN160101UK05', '9689177923') for _ in range(1)]

        # Act
        responses = send_messages_concurrently(messages, interaction_id='QUPC_IN160101UK05', sync_async=True)

        # Assert
        all_sync_async_states = MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()
        if has_errors(responses):
            # TODO: NIAD-72 remove prints and has_errors once sync-async feature is stable
            print('--- mhs-sync-async-state table ---')
            print(json.dumps(all_sync_async_states, indent=2))
        assert_all_messages_succeeded(responses)
        sync_async_state_assertor = DynamoSyncAsyncMhsTableStateAssertor(all_sync_async_states)
        for message, message_id in messages:
            hl7_xml_message_assertor = sync_async_state_assertor.assert_single_item_exists_with_key(message_id)
            self.assertions.hl7_xml_contains_response_code_and_patient_id(hl7_xml_message_assertor)
