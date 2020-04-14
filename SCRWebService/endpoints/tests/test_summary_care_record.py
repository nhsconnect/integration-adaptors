"""Tests associated with the Summary Care Record endpoint"""
import json
import pathlib

from builder.pystache_message_builder import MessageGenerationError
from utilities import file_utilities, test_utilities
from definitions import ROOT_DIR
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from unittest import mock
from endpoints import summary_care_record

GP_SUMMARY_UPLOAD_URL = "/gp_summary_upload"

complete_data_path = pathlib.Path(ROOT_DIR) / 'endpoints' / 'tests' / 'data' / 'complete_input.json'


class TestSummaryCareRecord(AsyncHTTPTestCase):
    """Tests associated with the Summary Care Record endpoint"""
    
    def get_app(self):
        self.forwarder = mock.MagicMock()

        return Application([
            (r'/gp_summary_upload', summary_care_record.SummaryCareRecord,
             dict(forwarder=self.forwarder))
        ])

    @mock.patch('utilities.message_utilities.get_uuid')
    def test_handler_returns_message_processing_response(self, uuid_mock):
        uuid_mock.return_value = "check123"
        body = file_utilities.get_file_dict(complete_data_path)
        response_mock = {'data': "Nice response message"}
        self.forwarder.forward_message_to_mhs.return_value = test_utilities.awaitable(response_mock)
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={'interaction-name': '123'},
                              body=json.dumps(body))

        self.forwarder.forward_message_to_mhs.assert_called_once_with("123", body, None, "check123")
        self.assertEqual(json.loads(response.body.decode()), {'data': "Nice response message"})

    def test_null_body_request_fails(self):
        body = ''
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', body=body)

        self.assertEqual(response.code, 400)
        self.assertIn('Exception raised while parsing message body: Expecting value: line 1 column 1',
                      response.body.decode())

    def test_invalid_json_request_fails(self):
        body = "{'yes': 'wow'}"
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={'interaction-name': '123'},
                              body=body)
        self.assertEqual(response.code, 400)
        error = "Exception raised while parsing message body:" \
                " Expecting property name enclosed in double quotes: line 1 column 2"
        self.assertIn(error, response.body.decode())

    def test_message_generation_exception_in_handler_returns_error_to_caller(self):
        body = file_utilities.get_file_dict(complete_data_path)
        self.forwarder.forward_message_to_mhs.side_effect = MessageGenerationError('This is a specific error')
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={'interaction-name': '123'},
                              body=json.dumps(body))

        self.assertEqual(response.code, 400)
        self.assertIn('This is a specific error', response.body.decode())
