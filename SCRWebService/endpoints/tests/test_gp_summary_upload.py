import json
import pathlib

from builder.pystache_message_builder import MessageGenerationError
from utilities import file_utilities
from definitions import ROOT_DIR
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from unittest import mock
from endpoints import gp_summary_upload

GP_SUMMARY_UPLOAD_URL = "/gp_summary_upload"

complete_data_path = pathlib.Path(ROOT_DIR) / 'endpoints' / 'tests' / 'data' / 'complete_input.json'


class TestGpSummaryUploadHandler(AsyncHTTPTestCase):

    def get_app(self):
        self.handler = mock.MagicMock()

        return Application([
            (r'/gp_summary_upload', gp_summary_upload.GpSummaryUpload,
             dict(handler=self.handler))
        ])

    def test_handler_happy_path(self):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)
        self.handler.forward_message_to_mhs.return_value = "Nice response message"
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={'interaction-id': '123'},
                              body=json.dumps(body))

        self.assertEqual(response.body.decode(), "Nice response message")

    def test_handler_empty_body(self):
        body = ''
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', body=body)

        self.assertEqual(response.code, 400)
        self.assertIn('Failed to parse json body from request', response.body.decode())

    def test_handler_invalid_json(self):
        body = "{'yes': 'wow'}"
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={'interaction-id': '123'},
                              body=body)
        self.assertEqual(response.code, 400)
        error = "Failed to parse json body from request: Expecting property name enclosed in double quotes"
        self.assertIn(error, response.body.decode())

    def test_message_generation_exception_in_handler(self):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)
        self.handler.forward_message_to_mhs.side_effect = MessageGenerationError('This is a specific error')
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={'interaction-id': '123'},
                              body=json.dumps(body))

        self.assertEqual(response.code, 400)
        self.assertIn('This is a specific error', response.body.decode())