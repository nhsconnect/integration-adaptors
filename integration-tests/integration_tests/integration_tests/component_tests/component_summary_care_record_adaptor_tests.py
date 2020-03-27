"""Component tests related to the Summary Care Record adaptor"""

from unittest import TestCase
from unittest import skip

from integration_tests.helpers.build_message import build_message
from integration_tests.http.scr_http_request_builder import ScrHttpRequestBuilder


class SummaryCareRecordAdaptorTests(TestCase):
    """
    These tests show a response from the SCR Adaptor
    They make use of the fake-spine service, which has known responses for certain message ids.
    They make use of the fake-spine-route-lookup service, which has known responses for certain interaction ids.
    """
    @skip('SCR test is not part of MHS adapter')
    def test_should_return_a_bad_request_to_the_client_when_the_client_provides_a_bad_request(self):
        # Arrange
        scr_json, message_id = build_message('bad_gp_summary_upload_json', patient_nhs_number='9689174606',
                                             message_id='AD7D39A8-1B6C-4520-8367-6B7BEBD7B842')

        # Act
        response = ScrHttpRequestBuilder() \
            .with_headers(interaction_name='SCR_GP_SUMMARY_UPLOAD',
                          message_id='AD7D39A8-1B6C-4520-8367-6B7BEBD7B842',
                          correlation_id='2') \
            .with_body(scr_json) \
            .execute_post_expecting_bad_request_response()

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn('Error whilst generating message', response.text)

    @skip('SCR test is not part of MHS adapter')
    def test_should_return_a_500_to_client_when_mhs_returns_500_to_SCR(self):
        # Arrange
        scr_json, message_id = build_message('json_16UK05', patient_nhs_number='9689174606',
                                             message_id='AD7D39A8-1B6C-4520-8367-6B7BEBD7B842')

        # Act
        response = ScrHttpRequestBuilder() \
            .with_headers(interaction_name='SCR_GP_SUMMARY_UPLOAD',
                          message_id='AD7D39A8-1B6C-4520-8367-6B7BEBD7B842',
                          correlation_id='2') \
            .with_body(scr_json) \
            .execute_post_expecting_internal_server_error()

        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertIn('Error whilst attempting to send the message to the MHS', response.text)
