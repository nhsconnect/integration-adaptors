"""A set of component tests that ties multiple parts of the SCR Adaptor together"""
import json
import pathlib
from unittest import mock

from scr import gp_summary_upload
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from utilities import file_utilities, test_utilities, xml_utilities

from definitions import ROOT_DIR
from endpoints import summary_care_record
from message_handling import message_sender, message_forwarder

GP_SUMMARY_UPLOAD_URL = "/"

data_path = pathlib.Path(ROOT_DIR) / 'endpoints' / 'tests' / 'data'
complete_data_path = data_path / 'complete_input.json'
populated_message_path = data_path / 'populated_message_template.xml'
response_xml = data_path / 'success_response.xml'

CORRELATION_ID = 'correlation-id'
MESSAGE_ID = 'message-id'
INTERACTION_NAME = 'interaction-name'
GP_SUMMARY_UPLOAD_NAME = 'SCR_GP_SUMMARY_UPLOAD'


class TestResponse(object):
    body = None


class TestSummaryCareRecord(AsyncHTTPTestCase):
    """Tests associated with the Summary Care Record adaptor"""

    def get_app(self):
        interactions = {
            GP_SUMMARY_UPLOAD_NAME: gp_summary_upload.GpSummaryUpload()
        }
        self.address = 'http://Fixed-Address.com'
        sender = message_sender.MessageSender(self.address)
        forwarder = message_forwarder.MessageForwarder(interactions, sender)

        return Application([(r"/", summary_care_record.SummaryCareRecord, dict(forwarder=forwarder))])

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_scr_adaptor_calls_mhs_end_point_with_populated_message(self, request_mock):
        # Arrange
        body = file_utilities.get_file_dict(complete_data_path)
        expected_message = file_utilities.get_file_string(populated_message_path)

        # Act
        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME},
                   body=json.dumps(body))

        # Assert
        body_call_value = json.loads(request_mock.call_args[1]['body'])
        call_method = request_mock.call_args[1]['method']
        url_method = request_mock.call_args[1]['url']

        xml_utilities.XmlUtilities.assert_xml_equal(body_call_value['payload'], expected_message)
        self.assertEqual(call_method, 'POST')
        self.assertEqual(url_method, self.address)

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_exception_raised_during_message_sending_raises_MessageSendingError(self, request_mock):
        body = file_utilities.get_file_dict(complete_data_path)
        request_mock.side_effect = Exception('Failed to route the dam packet')

        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                              headers={INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME},
                              body=json.dumps(body))

        self.assertEqual(response.code, 500)
        self.assertIn('Failed to route the dam packet', response.body.decode())

    def test_empty_interaction_name_raises_error(self):
        body = file_utilities.get_file_dict(complete_data_path)

        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={},
                              body=json.dumps(body))

        self.assertEqual(response.code, 400)
        self.assertIn('No interaction-name header provided', response.body.decode())

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_application_json_content_type_is_passed_to_mhs(self, request_mock):
        body = file_utilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME},
                   body=json.dumps(body))

        content_type_header = request_mock.call_args[1]['headers']['Content-Type']
        self.assertEqual(content_type_header, "application/json")

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_correlation_id_is_passed_to_mhs_if_provided_to_scr_adaptor(self, request_mock):
        body = file_utilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={
                       INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME,
                       CORRELATION_ID: "123123123"
                   },
                   body=json.dumps(body))

        correlation_id_header = request_mock.call_args[1]['headers'][CORRELATION_ID]
        self.assertEqual(correlation_id_header, "123123123")

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_message_id_is_passed_to_mhs_if_provided_to_scr_adaptor(self, request_mock):
        body = file_utilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={
                       INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME,
                       MESSAGE_ID: "123123123"
                   },
                   body=json.dumps(body))

        correlation_id_header = request_mock.call_args[1]['headers'][MESSAGE_ID]
        self.assertEqual(correlation_id_header, "123123123")

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_both_message_id_and_correlation_are_passed_to_mhs_when_provided(self, request_mock):
        body = file_utilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={
                       INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME,
                       MESSAGE_ID: 'messageId1212',
                       CORRELATION_ID: 'correlationId1212'
                   },
                   body=json.dumps(body))

        correlation_id_header = request_mock.call_args[1]['headers']['correlation-id']
        message_id_header = request_mock.call_args[1]['headers']['message-id']
        self.assertEqual(message_id_header, "messageId1212")
        self.assertEqual(correlation_id_header, 'correlationId1212')

    @mock.patch('utilities.message_utilities.get_uuid')
    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_when_no_correlation_id_is_provided_the_adaptor_generates_one_and_passes_it_to_the_mhs(self,
                                                                                                   request_mock,
                                                                                                   uuid_mock):
        uuid_mock.return_value = "yes-this-is-mocked"
        body = file_utilities.get_file_dict(complete_data_path)

        request_mock.return_value = test_utilities.awaitable("Response message")

        self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                   headers={
                       INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME,
                       MESSAGE_ID: 'messageId1212'
                   },
                   body=json.dumps(body))

        correlation_id_header = request_mock.call_args[1]['headers'][CORRELATION_ID]
        self.assertEqual(correlation_id_header, "yes-this-is-mocked")

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_should_correct_parse_success_response(self, request_mock):
        # Arrange
        body = file_utilities.get_file_dict(complete_data_path)
        response_body = file_utilities.get_file_string(response_xml)
        response_mock = TestResponse()
        response_mock.body = response_body
        request_mock.return_value = test_utilities.awaitable(response_mock)

        # Act
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                              headers={INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME},
                              body=json.dumps(body))

        response_body = json.loads(response.body.decode())

        self.assertEqual(response_body['messageRef'], '9C534C19-C587-4463-9AED-B76F715D3EA3')
        self.assertEqual(response_body['messageId'], '2E372546-229A-483F-9B11-EF46ABF3178C')
        self.assertEqual(response_body['creationTime'], '20190923112609')
        self.assertEqual(response_body['messageDetail'], 'GP Summary upload successful')

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_should_return_error_message_when_bad_response_body_is_returned(self, request_mock):
        # Arrange
        body = file_utilities.get_file_dict(complete_data_path)
        response_mock = TestResponse()
        response_mock.body = "This is a bad response to parse"
        request_mock.return_value = test_utilities.awaitable(response_mock)

        # Act
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST',
                              headers={INTERACTION_NAME: GP_SUMMARY_UPLOAD_NAME},
                              body=json.dumps(body))

        response_body = json.loads(response.body.decode())

        # Assert
        self.assertEqual(response_body['error'], 'Failed to parse response from xml provided')
