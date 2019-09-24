from unittest import TestCase
from integration_tests.helpers.build_message import build_message
from integration_tests.helpers.methods import get_asid
from integration_tests.http.scr_http_request_builder import ScrHttpRequestBuilder
from integration_tests.json.json_assertor import JsonResponseAssertor
from integration_tests.dynamo.dynamo import MHS_STATE_TABLE_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo import MHS_STATE_TABLE_DYNAMO_WRAPPER, MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.dynamo.dynamo_sync_async_mhs_table import DynamoSyncAsyncMhsTableStateAssertor


class ScrAdaptorTests(TestCase):
    """
    These tests show a sync-async response from spine via the SCR adaptor (and transitively the MHS) for the
    example message Gp Summary Upload.

    - Input: A json payload of the required details used to populate the REPC_IN150016UK05 template
        within the SCR adaptor
    - Expected Response:  A json dictionary of the key details parsed from a MCCI_IN010000UK13 success response

    An example of an expected success response is as follows:
        - {
            "messageRef": "1E2C0BB8-A0AE-4B65-A2EE-AE062F36FFB9",
            "messageId": "0CA0BB71-067A-49A4-AF9F-B4E19106F1C6",
            "creationTime": "20190924132325",
            "messageDetail": "GP Summary upload successful"
         }


     This is the same message pattern used by the async-reliable message, details of the flow are documented:
    - https://data.developer.nhs.uk/dms/mim/6.3.01/Index.htm
        -> Domains - Health and Clinical Management
            -> GP Summary
                -> 7.2 (Request)
            -> Infrastructure
                -> 4.2 (Response)
    """

    def setUp(self):
        MHS_STATE_TABLE_DYNAMO_WRAPPER.clear_all_records_in_table()

    def test_should_return_success_response_from_spine_as_json(self):
        # Arrange
        scr_json, message_id = build_message('json_16UK05', get_asid(), '9689174606', 'Scr GP Summary Upload test')

        # Act
        response = ScrHttpRequestBuilder() \
            .with_headers(interaction_name='SCR_GP_SUMMARY_UPLOAD',
                          message_id=message_id,
                          correlation_id='2') \
            .with_body(scr_json) \
            .execute_post_expecting_success()

        # Assert
        JsonResponseAssertor(response.text) \
            .assert_element_exists('messageId') \
            .assert_element_exists('creationTime') \
            .assert_key_value('messageRef', message_id) \
            .assert_key_value('messageDetail', 'GP Summary upload successful')

    def test_should_record_the_correct_response_between_inbound_and_outbound_components(self):
        # Arrange
        scr_json, message_id = build_message('json_16UK05', get_asid(), '9689174606', 'Scr GP Summary Upload test')

        # Act
        ScrHttpRequestBuilder() \
            .with_headers(interaction_name='SCR_GP_SUMMARY_UPLOAD',
                          message_id=message_id,
                          correlation_id='3') \
            .with_body(scr_json) \
            .execute_post_expecting_success()

        # Assert
        DynamoSyncAsyncMhsTableStateAssertor(MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_element_exists_with_value('.//requestSuccessDetail//detail', 'GP Summary upload successful')
