import json

import tornado.testing
from tornado.web import Application

from outbound.request import handler

REQUEST_BODY_PAYLOAD = "A request"
REQUEST_BODY = json.dumps({"payload": REQUEST_BODY_PAYLOAD})


class TestHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return tornado.web.Application([(r'/fhir/Patient/.*', handler.Handler)])

    def test_valid_post_any_request_line_return_202_response_code(self):

        response = self.fetch(r'/fhir/Patient/abc', method="POST",
                              body=REQUEST_BODY)

        self.assertEqual(202, response.code)

    def test_invalid_post_request_line_return_404_response_code(self):

        response = self.fetch(r'/fhir/', method="POST",
                              body=REQUEST_BODY)

        self.assertEqual(404, response.code)

