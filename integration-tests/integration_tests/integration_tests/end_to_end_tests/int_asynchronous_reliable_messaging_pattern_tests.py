"""
Provides tests around the Asynchronous Reliable workflow, including sync-async wrapping
"""
import json
from unittest import TestCase

from integration_tests.amq.amq_message_assertor import AMQMessageAssertor
from integration_tests.amq.mhs_inbound_queue import MHS_INBOUND_QUEUE
from integration_tests.assertors.assert_with_retries import AssertWithRetries
from integration_tests.db.db_wrapper_factory import MHS_STATE_TABLE_WRAPPER, MHS_SYNC_ASYNC_TABLE_WRAPPER
from integration_tests.db.mhs_table import MhsTableStateAssertor
from integration_tests.db.sync_async_mhs_table import SyncAsyncMhsTableStateAssertor
from integration_tests.end_to_end_tests.common_assertions import CommonAssertions
from integration_tests.helpers.build_message import build_message
from integration_tests.helpers.concurrent_requests import send_messages_concurrently, \
    assert_all_messages_succeeded, has_errors
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
        MHS_STATE_TABLE_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_WRAPPER.clear_all_records_in_table()
        MHS_INBOUND_QUEUE.drain()
        self.assertions = CommonAssertions('async-reliable')

    def _assert_gp_summary_upload_success_detail_is_present(self, hl7_xml_assertor: Hl7XmlResponseAssertor):
        hl7_xml_assertor.assert_element_exists_with_value('.//requestSuccessDetail//detail', 'GP Summary upload successful')

    def test_should_return_successful_response_from_spine_to_message_queue(self):
        # Arrange
        message, message_id = build_message('REPC_IN150016UK05', '9446245796')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='REPC_IN150016UK05',
                          message_id=message_id,
                          wait_for_response=False,
                          correlation_id='1') \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        amq_assertor = AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue())
        self.assertions.spline_reply_published_to_message_queue(amq_assertor, message_id)
        hl7_xml_assertor = amq_assertor.assertor_for_hl7_xml_message()
        self._assert_gp_summary_upload_success_detail_is_present(hl7_xml_assertor)

    def test_should_record_asynchronous_reliable_message_status_as_successful(self):
        # Arrange
        message, message_id = build_message('REPC_IN150016UK05', '9446245796')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='REPC_IN150016UK05',
                          message_id=message_id,
                          wait_for_response=False,
                          correlation_id='1') \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        hl7_xml_assertor = AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue())\
            .assertor_for_hl7_xml_message()
        self._assert_gp_summary_upload_success_detail_is_present(hl7_xml_assertor)

        AssertWithRetries(retry_count=10) \
            .assert_condition_met(lambda: MhsTableStateAssertor.wait_for_inbound_response_processed(message_id))

        dynamo_assertor = MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table())
        self.assertions.message_status_recorded_as_successfully_processed(dynamo_assertor, message_id)

    def test_should_return_successful_response_and_record_spline_reply_in_resync_table_if_wait_for_response_requested(self):
        # Arrange
        messages = [build_message('REPC_IN150016UK05', '9446245796') for i in range(1)]

        # Act
        responses = send_messages_concurrently(messages, interaction_id='REPC_IN150016UK05', wait_for_response=True)

        # Assert
        all_sync_async_states = MHS_SYNC_ASYNC_TABLE_WRAPPER.get_all_records_in_table()
        assert_all_messages_succeeded(responses)
        sync_async_state_assertor = SyncAsyncMhsTableStateAssertor(all_sync_async_states)
        for message, message_id in messages:
            hl7_xml_assertor = sync_async_state_assertor \
                .assert_single_item_exists_with_key(message_id)
            self._assert_gp_summary_upload_success_detail_is_present(hl7_xml_assertor)
