from unittest import TestCase, skip
from integration_tests.helpers.build_message import build_message
from integration_tests.http.scr_http_request_builder import ScrHttpRequestBuilder
from integration_tests.json.json_assertor import JsonResponseAssertor


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

    @skip('SCR test is not part of MHS adapter')
    def test_should_return_success_response_from_spine_as_json(self):
        # Arrange
        scr_json, message_id = build_message('json_16UK05', patient_nhs_number='9691813343')

        # Act
        response = ScrHttpRequestBuilder() \
            .with_headers(interaction_name='SCR_GP_SUMMARY_UPLOAD',
                          message_id=message_id,
                          correlation_id='2') \
            .with_body(scr_json) \
            .execute_post_expecting_success()

        # Assert
        JsonResponseAssertor(response.text) \
            .assert_key_exists('messageId') \
            .assert_key_exists('creationTime') \
            .assert_key_exists_with_value('messageRef', message_id) \
            .assert_key_exists_with_value('messageDetail', 'GP Summary upload successful')


