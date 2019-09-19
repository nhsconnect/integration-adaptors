"""A set of component tests that ties multiple parts of the SCR Adaptor together"""
import json
import pathlib
from scr import gp_summary_upload
from utilities import file_utilities, test_utilities, xml_utilities
from definitions import ROOT_DIR
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from unittest import mock
from endpoints import summary_care_record
from message_handling import message_sender, message_forwarder

GP_SUMMARY_UPLOAD_URL = "/"

complete_data_path = pathlib.Path(ROOT_DIR) / 'endpoints' / 'tests' / 'data' / 'complete_input.json'
populated_message_path = pathlib.Path(ROOT_DIR) / 'endpoints' / 'tests' / 'data' / 'populated_message_template.xml'


class TestSummaryCareRecord(AsyncHTTPTestCase):
    """Tests associated with the Summary Care Record adaptor"""

    def get_app(self):
        interactions = {
            'SCR_GP_SUMMARY_UPLOAD': gp_summary_upload.GpSummaryUpload()
        }
        self.address = 'http://Fixed-Address.com'
        sender = message_sender.MessageSender(self.address)
        forwarder = message_forwarder.MessageForwarder(interactions, sender)

        return Application([(r"/", summary_care_record.SummaryCareRecord, dict(forwarder=forwarder))])

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_scr_adaptor_calls_mhs_end_point_happy_path(self, request_mock):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)
        expected_message = file_utilities.FileUtilities.get_file_string(populated_message_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                              headers={'interaction-name': 'SCR_GP_SUMMARY_UPLOAD'},
                              body=json.dumps(body))

        body_call_value = request_mock.call_args[1]['body']
        call_method = request_mock.call_args[1]['method']
        url_method = request_mock.call_args[1]['url']

        xml_utilities.XmlUtilities.assert_xml_equal(body_call_value, expected_message)
        self.assertEqual(call_method, 'POST')
        self.assertEqual(url_method, self.address)

        self.assertEqual(response.body.decode(), "Response message")

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_exception_raised_during_message_sending_raises_MessageSendingError(self, request_mock):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)
        request_mock.side_effect = Exception('Failed to route the dam packet')

        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                              headers={'interaction-name': 'SCR_GP_SUMMARY_UPLOAD'},
                              body=json.dumps(body))

        self.assertEqual(response.code, 500)
        self.assertIn('Failed to route the dam packet', response.body.decode())

    def test_empty_interaction_name_raises_error(self):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)

        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={},
                              body=json.dumps(body))

        self.assertEqual(response.code, 400)
        self.assertIn('No interaction-name header provided', response.body.decode())

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_correlation_id_is_passed_to_mhs(self, request_mock):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={
                       'interaction-name': 'SCR_GP_SUMMARY_UPLOAD',
                       'correlation-id': "123123123"
                   },
                   body=json.dumps(body))

        correlation_id_header = request_mock.call_args[1]['headers']['correlation-id']
        self.assertEqual(correlation_id_header, "123123123")

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_message_id_is_passed_to_mhs(self, request_mock):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={
                       'interaction-name': 'SCR_GP_SUMMARY_UPLOAD',
                       'message-id': "123123123"
                   },
                   body=json.dumps(body))

        correlation_id_header = request_mock.call_args[1]['headers']['message-id']
        self.assertEqual(correlation_id_header, "123123123")

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_both_message_id_and_correlation_are_passed_to_mhs(self, request_mock):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={
                       'interaction-name': 'SCR_GP_SUMMARY_UPLOAD',
                       'message-id': 'messageId1212',
                       'correlation-id': 'correlationId1212'
                   },
                   body=json.dumps(body))

        correlation_id_header = request_mock.call_args[1]['headers']['correlation-id']
        message_id_header = request_mock.call_args[1]['headers']['message-id']
        self.assertEqual(message_id_header, "messageId1212")
        self.assertEqual(correlation_id_header, 'correlationId1212')

    @mock.patch('utilities.message_utilities.MessageUtilities.get_uuid')
    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_when_no_correlation_id_is_provided_the_adaptor_generates_one_and_passes_it_to_the_mhs(self,
                                                                                                   request_mock,
                                                                                                   uuid_mock):
        uuid_mock.return_value = "yes-this-is-mocked"
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={
                       'interaction-name': 'SCR_GP_SUMMARY_UPLOAD',
                       'message-id': 'messageId1212'
                   },
                   body=json.dumps(body))

        correlation_id_header = request_mock.call_args[1]['headers']['correlation-id']
        self.assertEqual(correlation_id_header, "yes-this-is-mocked")

