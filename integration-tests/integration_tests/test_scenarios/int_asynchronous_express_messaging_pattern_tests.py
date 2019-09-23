"""
Provides tests around the Asynchronous Express workflow, including sync-async wrapping
"""
from unittest import TestCase

from integration_tests.amq.amq import MHS_INBOUND_QUEUE
from integration_tests.amq.amq_message_assertor import AMQMessageAssertor
from integration_tests.assertors.assert_with_retries import AssertWithRetries
from integration_tests.dynamo.dynamo import MHS_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.helpers.build_message import build_message
from integration_tests.helpers.methods import get_asid
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder
from integration_tests.xml.hl7_xml_assertor import Hl7XmlResponseAssertor


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
        MHS_DYNAMO_WRAPPER.clear_all_records_in_table()

    def test_should_return_successful_response_from_spine_to_message_queue(self):
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', get_asid(), '9689177923', 'Asynchronous Express test')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05',
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
            .assert_element_attribute('.//queryAck//queryResponseCode', 'code', 'OK') \
            .assert_element_attribute('.//patient//id', 'extension', '9689177923')

    def test_should_record_asynchronous_express_message_status_as_successful(self):
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', get_asid(), '9689177923',
                                            'Asynchronous Express test')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05',
                          message_id=message_id,
                          sync_async=False,
                          correlation_id='1') \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue()) \
            .assertor_for_hl7_xml_message() \
            .assert_element_attribute('.//queryAck//queryResponseCode', 'code', 'OK')

        AssertWithRetries(retry_count=10)\
            .assert_condition_met(lambda: self.wait_for_inbound_response_processed(message_id))

        DynamoMhsTableStateAssertor(MHS_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values({
            'INBOUND_STATUS': 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED',
            'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_ACKD',
            'WORKFLOW': 'async-express'
        })

    def test_should_return_successful_response_from_spine_in_original_post_request_body_if_sync_async_requested(self):
        # Arrange
        message, message_id = build_message('QUPC_IN160101UK05', get_asid(), '9689177923', 'Asynchronous Express test')

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPC_IN160101UK05', message_id=message_id, sync_async=True) \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        Hl7XmlResponseAssertor(response.text) \
            .assert_element_attribute('.//queryAck//queryResponseCode', 'code', 'OK') \
            .assert_element_attribute('.//patient//id', 'extension', '9689177923')

    @staticmethod
    def wait_for_inbound_response_processed(message_id: str) -> bool:
        return DynamoMhsTableStateAssertor(MHS_DYNAMO_WRAPPER.get_all_records_in_table())\
            .assert_single_item_exists_with_key(message_id)\
            .item_contains_value('INBOUND_STATUS', 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED')
