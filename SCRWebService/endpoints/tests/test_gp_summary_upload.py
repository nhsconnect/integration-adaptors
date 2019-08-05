import json
import pathlib

from utilities import file_utilities
from definitions import  ROOT_DIR
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from unittest.mock import Mock
from endpoints import gp_summary_upload

GP_SUMMARY_UPLOAD_URL = "/gp_summary_upload"

complete_data_path = pathlib.Path(ROOT_DIR) / 'endpoints' / 'tests' / 'data' / 'complete_input.json'


class TestGpSummaryUploadHandler(AsyncHTTPTestCase):

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r'/gp_summary_upload', gp_summary_upload.GpSummaryUpload, {})
        ])

    def test_handler_happy_path(self):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', body=json.dumps(body))
        self.assertEqual(json.dumps(json.loads(response.body)), json.dumps(body))

    def test_handler_missing_keys(self):
        body = '{}'
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', body=body)
        self.assertEqual(response.code, 500)

        self.assertEqual(response.body, str.encode('Exception raised whilst populating hl7 message with json: '
                                                   'Failed to find key:Id when generating message '
                                                   'from template file:16UK05'))

    def test_handler_empty_body(self):
        body = ''
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', body=body)
        self.assertEqual(response.code, 500)
        self.assertEqual(response.body, str.encode('Failed to parse message body:'
                                                   ' Expecting value: line 1 column 1 (char 0)'))

    def test_handler_invalid_json(self):
        body = "{'yes': 'wow'}"
        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', body=body)
        self.assertEqual(response.code, 500)
        self.assertEqual(response.body,
                         str.encode('Failed to parse message body: Expecting property '
                                    'name enclosed in double quotes: line 1 column 2 (char 1)'))
