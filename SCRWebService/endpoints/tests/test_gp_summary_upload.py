import json

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from tornado.httpserver import HTTPRequest
from unittest.mock import Mock
from endpoints import gp_summary_upload

class TestGpSummaryUploadHandler(AsyncHTTPTestCase):

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r"/gpsummaryupload", gp_summary_upload.GpSummaryUpload, {})
        ])

    def test_handler_happy_path(self):
        body = '{"test": "tested"}'
        response = self.fetch(f"/gpsummaryupload", method="POST", body=body)

        self.assertEqual(json.loads(response.body), json.loads(body))

    def test_handler_empty_dictionary(self):
        body = '{}'
        response = self.fetch(f"/gpsummaryupload", method="POST", body=body)

        self.assertEqual(json.loads(response.body), json.loads(body))

    def test_handler_empty_body(self):
        body = ''
        response = self.fetch(f"/gpsummaryupload", method="POST", body=body)
        self.assertEqual(response.code, 500)
        self.assertEqual(response.body, str.encode("Empty body received with post request"))
