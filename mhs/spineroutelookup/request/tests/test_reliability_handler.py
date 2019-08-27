import json
import unittest.mock

import tornado.httputil
import tornado.testing
import tornado.web
from utilities import test_utilities

from request import reliability_handler

ORG_CODE = "org"
SERVICE_ID = "service"
RELIABILITY_DETAILS = {"retries": 7}


class TestReliabilityRequestHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        self.routing = unittest.mock.Mock()

        return tornado.web.Application([
            (r"/", reliability_handler.ReliabilityRequestHandler, {"routing": self.routing})
        ])

    def test_get(self):
        self.routing.get_reliability.return_value = test_utilities.awaitable(RELIABILITY_DETAILS)

        url = tornado.httputil.url_concat("/", {"org-code": ORG_CODE, "service-id": SERVICE_ID})
        response = self.fetch(url, method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(RELIABILITY_DETAILS, json.loads(response.body))
        self.routing.get_reliability.assert_called_with(ORG_CODE, SERVICE_ID)
