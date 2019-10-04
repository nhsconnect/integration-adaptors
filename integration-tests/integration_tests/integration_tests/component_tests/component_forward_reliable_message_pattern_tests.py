"""Component tests related to the forward-reliable message pattern"""

import unittest

from integration_tests.assertors.text_error_response_assertor import TextErrorResponseAssertor
from integration_tests.dynamo.dynamo import MHS_STATE_TABLE_DYNAMO_WRAPPER, MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.helpers.build_message import build_message
from integration_tests.http.inbound_proxy_http_request_builder import InboundProxyHttpRequestBuilder
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder
from integration_tests.xml.eb_xml_assertor import EbXmlResponseAssertor


class ForwardReliablesMessagingPatternTests(unittest.TestCase):
    """
    These tests show an forward-reliable response from Spine via the MHS for the example message interaction
    of Common Content Forward Reliable GP2GP Large Message Attachment.

    They make use of the fake-spine service, which has known responses for certain message ids.
    They make use of the fake-spine-route-lookup service, which has known responses for certain interaction ids.
    """

    def setUp(self):
        MHS_STATE_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()

    def test_should_return_nack_when_forward_reliable_message_is_not_meant_for_the_mhs_system(self):
        # Arrange
        message, message_id = build_message('INBOUND_UNEXPECTED_MESSAGE', '9689177923')

        # Act
        response = InboundProxyHttpRequestBuilder()\
            .with_body(message)\
            .execute_post_expecting_success()

        # Assert
        EbXmlResponseAssertor(response.text)\
            .assert_element_attribute(".//ErrorList//Error", "errorCode", "ValueNotRecognized")\
            .assert_element_attribute(".//ErrorList//Error", "severity", "Error")\
            .assert_element_exists_with_value(".//ErrorList//Error//Description", "501314:Invalid To Party Type attribute")

    def test_should_return_successful_response_to_client_when_a_business_level_retry_is_required_and_succeeds(self):
        """
        Message ID: '35586865-45B0-41A5-98F6-817CA6F1F5EF' configured in fakespine to return a SOAP Fault error,
        after 2 retries fakespine will return a success response.
        """

        # Arrange
        message, message_id = build_message('COPC_IN000001UK01', '9689177923',
                                            message_id='35586865-45B0-41A5-98F6-817CA6F1F5EF'
                                            )
        # Act/Assert: Response should be 202
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01 ', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_success()

    def test_should_record_message_status_when_a_business_level_retry_is_required_and_succeeds(self):
        """
        Message ID: '35586865-45B0-41A5-98F6-817CA6F1F5EF' configured in fakespine to return a SOAP Fault error,
        after 2 retries fakespine will return a success response.
        """

        # Arrange
        message, message_id = build_message('COPC_IN000001UK01', '9689177923',
                                            message_id='35586865-45B0-41A5-98F6-817CA6F1F5EF'
                                            )
        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01 ', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        DynamoMhsTableStateAssertor(MHS_STATE_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_ACKD',
                'WORKFLOW': 'forward-reliable'
            })

    def test_should_return_information_from_soap_fault_returned_by_spine_in_original_post_request_to_client(self):
        """
        Message ID: 3771F30C-A231-4D64-A46C-E7FB0D52C27C configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('COPC_IN000001UK01', '9446245796', message_id='3771F30C-A231-4D64-A46C-E7FB0D52C27C')

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        TextErrorResponseAssertor(response.text) \
            .assert_error_code(200) \
            .assert_code_context('urn:nhs:names:error:tms') \
            .assert_severity('Error')
    
    def test_should_record_message_status_when_soap_fault_returned_from_spine(self):
        """
        Message ID: 3771F30C-A231-4D64-A46C-E7FB0D52C27C configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml
        """
        # Arrange
        message, message_id = build_message('COPC_IN000001UK01', '9446245796',
                                            message_id='3771F30C-A231-4D64-A46C-E7FB0D52C27C')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        DynamoMhsTableStateAssertor(MHS_STATE_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_NACKD',
                'WORKFLOW': 'forward-reliable'
            })

    def test_should_return_information_from_ebxml_fault_returned_by_spine_in_original_post_request_to_client(self):
        """
        Message ID: 'A7D43B03-38FB-4ED7-8D04-0496DBDEDB7D' configured in fakespine to return a ebxml fault
        """

        # Arrange
        message, message_id = build_message('COPC_IN000001UK01', '9689177923',
                                            message_id='A7D43B03-38FB-4ED7-8D04-0496DBDEDB7D'
                                            )
        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01 ', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        TextErrorResponseAssertor(response.text) \
            .assert_code_context('urn:oasis:names:tc:ebxml') \
            .assert_severity('Error') \
            .assert_error_type('ebxml_error')

    def test_should_record_message_status_when_ebxml_fault_returned_from_spine(self):
        """
        Message ID: 'A7D43B03-38FB-4ED7-8D04-0496DBDEDB7D' configured in fakespine to return a ebxml fault
        """

        # Arrange
        message, message_id = build_message('COPC_IN000001UK01', '9689177923',
                                            message_id='A7D43B03-38FB-4ED7-8D04-0496DBDEDB7D'
                                            )
        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01 ', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        DynamoMhsTableStateAssertor(MHS_STATE_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_NACKD',
                'WORKFLOW': 'forward-reliable'
            })
