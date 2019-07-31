import json

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from unittest.mock import Mock
from endpoints import gp_summary_upload


class TestGpSummaryUploadHandler(AsyncHTTPTestCase):

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r'/gpsummaryupload', gp_summary_upload.GpSummaryUpload, {})
        ])

    def test_handler_happy_path(self):
        body = '{"test": "tested"}'
        response = self.fetch(f'/gpsummaryupload', method='POST', body=body)

        self.assertEqual(json.loads(response.body), json.loads(body))

    def test_handler_empty_dictionary(self):
        body = '{}'
        response = self.fetch(f'/gpsummaryupload', method='POST', body=body)

        self.assertEqual(json.loads(response.body), json.loads(body))

    def test_handler_empty_body(self):
        body = ''
        response = self.fetch(f'/gpsummaryupload', method='POST', body=body)
        self.assertEqual(response.code, 500)
        self.assertEqual(response.body, str.encode('Failed to parse message body:'
                                                   ' Expecting value: line 1 column 1 (char 0)'))

    def test_handler_invalid_json(self):
        body = "{'yes': 'wow'}"
        response = self.fetch(f'/gpsummaryupload', method='POST', body=body)
        self.assertEqual(response.code, 500)
        self.assertEqual(response.body,
                         str.encode('Failed to parse message body: Expecting property '
                                    'name enclosed in double quotes: line 1 column 2 (char 1)'))
