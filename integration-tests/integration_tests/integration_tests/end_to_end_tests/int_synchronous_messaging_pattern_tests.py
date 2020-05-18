"""
Provides tests around the Synchronous workflow
"""
from unittest import TestCase

from integration_tests.dynamo.dynamo import MHS_STATE_TABLE_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.helpers.build_message import build_message
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder
from integration_tests.xml.hl7_xml_assertor import Hl7XmlResponseAssertor


class SynchronousMessagingPatternTests(TestCase):
    """
    These tests show a synchronous response from Spine via the MHS for the example message interaction of PDS
    (Personal Demographics Service).

    Synchronous message testing interaction:
    - Message sent: PDS Retrieval Query (QUPA_IN040000UK32)
    - Expected response: PDS Retrieval Query Successful (QUPA_IN050000UK32)

    Flow documented at:
    - https://data.developer.nhs.uk/dms/mim/4.2.00/Index.htm
        -> Domains
            -> PDS
                -> 6.4 (Request)
                -> 6.5 (Response)
    """

    def setUp(self):
        MHS_STATE_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()

    def test_should_return_successful_response_from_spine_in_original_post_request_body(self):
        # Arrange
        message, message_id = build_message('QUPA_IN040000UK32', '9691035456')

        print('-------------------------- msg: ')
        print(message)

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPA_IN040000UK32', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        Hl7XmlResponseAssertor(response.text) \
            .assert_element_exists('.//retrievalQueryResponse//QUPA_IN050000UK32//PdsSuccessfulRetrieval') \
            .assert_element_attribute('.//queryAck//queryResponseCode', 'code', 'OK') \
            .assert_element_attribute('.//patientRole//id', 'extension', '9691035456') \
            .assert_element_attribute('.//messageRef//id', 'root', message_id)

    def test_should_record_synchronous_message_status_as_successful(self):
        # Arrange
        message, message_id = build_message('QUPA_IN040000UK32', '9691035456')

        print('-------------------------- msg: ')
        print(message)

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPA_IN040000UK32', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        DynamoMhsTableStateAssertor(MHS_STATE_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values({
            'INBOUND_STATUS': None,
            'OUTBOUND_STATUS': 'SYNC_RESPONSE_SUCCESSFUL',
            'WORKFLOW': 'sync'
        })
