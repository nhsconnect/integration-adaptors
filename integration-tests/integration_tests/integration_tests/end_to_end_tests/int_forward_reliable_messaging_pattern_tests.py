"""
Provides tests around the Forward Reliable workflow, including sync-async wrapping
"""
from unittest import TestCase

from integration_tests.amq.amq_message_assertor import AMQMessageAssertor
from integration_tests.amq.mhs_inbound_queue import MHS_INBOUND_QUEUE
from integration_tests.assertors.assert_with_retries import AssertWithRetries
from integration_tests.db.db_wrapper_factory import MHS_STATE_TABLE_WRAPPER, MHS_SYNC_ASYNC_TABLE_WRAPPER
from integration_tests.db.mhs_table import MhsTableStateAssertor
from integration_tests.end_to_end_tests.common_assertions import CommonAssertions
from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder


class ForwardReliableMessagingPatternTests(TestCase):
    """
     These tests show forward reliable response from Spine via the MHS for the example message interaction of
     Common Content Forward Reliable GP2GP Large Message Attachment.

    Asynchronous message interaction:
    - Message sent: Common Content Forward Reliable (COPC_IN000001UK01)
    - Expected response: Application Acknowledgement (MCCI_IN010000UK13)

    Flow documented at:
    - https://gpitbjss.atlassian.net/wiki/spaces/RTDel/pages/1561165837/Document+Library?preview=/1561165837/1561198617/2087%20EIS11.6--Part%203--MessageInteractionMap.doc
        -> 3.22 Common Content
            -> 3.22.1.1 (Request)
            -> 3.22.1.1 (Response)

    The to_party_id, and to_asid are fixed values that the forward reliable responder in opentest will respond to.
    If failures are seen here, it is probably an issue with opentest SDS not being correctly configured for your account.
    """

    def setUp(self):
        MHS_STATE_TABLE_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_WRAPPER.clear_all_records_in_table()
        MHS_INBOUND_QUEUE.drain()
        self.assertions = CommonAssertions('forward-reliable')

    def test_should_return_successful_response_from_spine_to_message_queue(self):
        # Arrange
        message, message_id = build_message('COPC_IN000001UK01', to_party_id='X26-9199246', to_asid='918999199246')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01',
                          message_id=message_id,
                          wait_for_response=False,
                          correlation_id=message_id,
                          ods_code='X26') \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue()) \
            .assert_property('message-id', message_id) \
            .assert_property('correlation-id', message_id) \
            .assert_json_content_type() \
            .assertor_for_hl7_xml_message() \
            .assert_element_attribute('.//acknowledgement//messageRef//id', 'root', message_id)

    def test_should_record_forward_reliable_message_status_as_successful(self):
        # Arrange
        # The to_party_id, and to_asid are fixed values that the forward reliable responder in opentest will respond to.
        # If failures are seen here, it is probably an issue with opentest SDS not being correctly configured for your
        # account
        message, message_id = build_message('COPC_IN000001UK01', to_party_id='X26-9199246', to_asid='918999199246')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01',
                          message_id=message_id,
                          wait_for_response=False,
                          correlation_id=message_id,
                          ods_code='X26') \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue()) \
            .assertor_for_hl7_xml_message() \
            .assert_element_attribute('.//acknowledgement//messageRef//id', 'root', message_id)

        AssertWithRetries(retry_count=10) \
            .assert_condition_met(lambda: MhsTableStateAssertor.wait_for_inbound_response_processed(message_id))

        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values({
            'INBOUND_STATUS': 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED',
            'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_ACKD',
            'WORKFLOW': 'forward-reliable'
        })
