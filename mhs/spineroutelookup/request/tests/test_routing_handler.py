import json
import unittest.mock

import tornado.httputil
import tornado.testing
import tornado.web
from utilities import test_utilities

from request import routing_handler

ORG_CODE = "org"
SERVICE_ID = "service"
END_POINT_DETAILS = {"end_point": "http://www.example.com"}


class TestRoutingRequestHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        self.routing = unittest.mock.Mock()

        return tornado.web.Application([
            (r"/", routing_handler.RoutingRequestHandler, {"routing": self.routing})
        ])

    def test_get(self):
        self.routing.get_end_point.return_value = test_utilities.awaitable(END_POINT_DETAILS)

        url = tornado.httputil.url_concat("/", {"org-code": ORG_CODE, "service-id": SERVICE_ID})
        response = self.fetch(url, method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(END_POINT_DETAILS, json.loads(response.body))
        self.routing.get_end_point.assert_called_with(ORG_CODE, SERVICE_ID)
