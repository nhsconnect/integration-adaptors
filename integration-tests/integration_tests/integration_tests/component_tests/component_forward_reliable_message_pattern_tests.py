"""Component tests related to the forward-reliable message pattern"""

import unittest

from integration_tests.amq.amq_message_assertor import AMQMessageAssertor
from integration_tests.amq.mhs_inbound_queue import MHS_INBOUND_QUEUE
from integration_tests.assertors.json_error_response_assertor import JsonErrorResponseAssertor
from integration_tests.db.db_wrapper_factory import MHS_STATE_TABLE_WRAPPER, MHS_SYNC_ASYNC_TABLE_WRAPPER
from integration_tests.db.mhs_table import MhsTableStateAssertor
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
        MHS_STATE_TABLE_WRAPPER.clear_all_records_in_table()
        MHS_SYNC_ASYNC_TABLE_WRAPPER.clear_all_records_in_table()
        MHS_INBOUND_QUEUE.drain()

    def test_should_place_unsolicited_valid_message_onto_queue_for_client_to_receive(self):
        # Arrange
        message, message_id = build_message('INBOUND_UNEXPECTED_MESSAGE', '9689177923', to_party_id="test-party-key")

        # Act
        InboundProxyHttpRequestBuilder() \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        AMQMessageAssertor(MHS_INBOUND_QUEUE.get_next_message_on_queue()) \
            .assert_property('message-id', message_id)\
            .assertor_for_hl7_xml_message()\
            .assert_element_attribute(".//ControlActEvent//code", "displayName", "GP2GP Large Message Attachment Information")

    def test_should_return_nack_when_forward_reliable_message_is_not_meant_for_the_mhs_system(self):
        # Arrange
        message, message_id = build_message('INBOUND_UNEXPECTED_MESSAGE', '9689177923', to_party_id="NOT_THE_MHS")

        # Act
        response = InboundProxyHttpRequestBuilder()\
            .with_body(message)\
            .execute_post_expecting_success()

        # Assert
        EbXmlResponseAssertor(response.text)\
            .assert_element_attribute(".//ErrorList//Error", "errorCode", "ValueNotRecognized")\
            .assert_element_attribute(".//ErrorList//Error", "severity", "Error")\
            .assert_element_exists_with_value(".//ErrorList//Error//Description", "501314:Invalid To Party Type attribute")

    def test_should_return_500_response_when_inbound_service_receives_message_in_invalid_format(self):
        # Arrange
        message, message_id = build_message('INBOUND_UNEXPECTED_INVALID_MESSAGE', '9689177923')

        # Act
        response = InboundProxyHttpRequestBuilder() \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        self.assertIn('Exception during inbound message parsing', response.text)

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
            .with_headers(interaction_id='COPC_IN000001UK01 ', message_id=message_id, wait_for_response=False) \
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
            .with_headers(interaction_id='COPC_IN000001UK01 ', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
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
            .with_headers(interaction_id='COPC_IN000001UK01', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
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
            .with_headers(interaction_id='COPC_IN000001UK01', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
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
            .with_headers(interaction_id='COPC_IN000001UK01 ', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
            .assert_code_context('urn:oasis:names:tc:ebxml-msg:service:errors') \
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
            .with_headers(interaction_id='COPC_IN000001UK01 ', message_id=message_id, wait_for_response=False) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values(
            {
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_NACKD',
                'WORKFLOW': 'forward-reliable'
            })

    def test_should_return_information_from_soap_fault_returned_from_spine_in_original_post_request_when_wait_for_response_requested(self):
        """
        Message ID: 3771F30C-A231-4D64-A46C-E7FB0D52C27C configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml

        Here we use 'PRSC_IN080000UK07' which is an eRS slot polling call, it is a forward reliable message type that
        can be wrapped in wait_for_response
        """
        # Arrange
        message, message_id = build_message('PRSC_IN080000UK07', '9446245796', message_id='3771F30C-A231-4D64-A46C-E7FB0D52C27C')

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='PRSC_IN080000UK07', message_id=message_id, wait_for_response=True) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
            .assert_error_code(200) \
            .assert_code_context('urn:nhs:names:error:tms') \
            .assert_severity('Error')

    def test_should_update_status_when_a_soap_fault_is_returned_from_spine_and_wait_for_response_is_requested(self):
        """
        Message ID: 3771F30C-A231-4D64-A46C-E7FB0D52C27C configured in fakespine to return a SOAP Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/soap_fault_single_error.xml

        Here we use 'PRSC_IN080000UK07' which is an eRS slot polling call, it is a forward reliable message type that
        can be wrapped in sync-async
        """
        # Arrange
        message, message_id = build_message('PRSC_IN080000UK07', '9446245796',
                                            message_id='3771F30C-A231-4D64-A46C-E7FB0D52C27C')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='PRSC_IN080000UK07', message_id=message_id, wait_for_response=True) \
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

    def test_should_return_information_from_an_ebxml_fault_returned_from_spine_in_original_post_request_when_wait_for_response_requested(self):
        """
        Message ID: 'A7D43B03-38FB-4ED7-8D04-0496DBDEDB7D' configured in fakespine to return a ebxml fault

        Here we use 'PRSC_IN080000UK07' which is an eRS slot polling call, it is a forward reliable message type that
        can be wrapped in wait_for_response
        """

        # Arrange
        message, message_id = build_message('PRSC_IN080000UK07', '9689177923',
                                            message_id='A7D43B03-38FB-4ED7-8D04-0496DBDEDB7D'
                                            )
        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='PRSC_IN080000UK07 ', message_id=message_id, wait_for_response=True) \
            .with_body(message) \
            .execute_post_expecting_error_response()

        # Assert
        JsonErrorResponseAssertor(response.text) \
            .assert_code_context('urn:oasis:names:tc:ebxml-msg:service:errors') \
            .assert_severity('Error') \
            .assert_error_type('ebxml_error')

    def test_should_update_status_when_a_ebxml_fault_is_returned_from_spine_and_wait_for_response_is_requested(self):
        """
        Message ID: A7D43B03-38FB-4ED7-8D04-0496DBDEDB7D configured in fakespine to return a ebxml Fault error.
        Error found here: fake_spine/fake_spine/configured_responses/ebxml_fault_single_error.xml

        Here we use 'PRSC_IN080000UK07' which is an eRS slot polling call, it is a forward reliable message type that
        can be wrapped in wait_for_response
        """
        # Arrange
        message, message_id = build_message('PRSC_IN080000UK07', '9446245796',
                                            message_id='3771F30C-A231-4D64-A46C-E7FB0D52C27C')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='PRSC_IN080000UK07', message_id=message_id, wait_for_response=True) \
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
        message, message_id = build_message('COPC_IN000001UK01')

        # attachment with content type that is not permitted
        attachments = [{
            'content_type': 'application/zip',
            'is_base64': False,
            'description': 'Some description',
            'payload': 'Some payload'
        }]

        # Act
        response = MhsHttpRequestBuilder() \
            .with_headers(interaction_id='COPC_IN000001UK01', message_id=message_id, wait_for_response=False) \
            .with_body(message, attachments=attachments) \
            .execute_post_expecting_bad_request_response()

        # Assert
        self.assertEqual(response.text, "400: Invalid request. Validation errors: {'attachments': {0: "
                                        "{'content_type': ['Must be one of: text/plain, text/html, application/pdf, "
                                        "text/xml, application/xml, text/rtf, audio/basic, audio/mpeg, image/png, "
                                        "image/gif, image/jpeg, image/tiff, video/mpeg, application/msword, "
                                        "application/octet-stream.']}}}")
