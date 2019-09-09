import json

import tornado.testing
import tornado.web
from utilities import test_utilities

from request import routing_handler
from request.tests import test_request_handler

END_POINT_DETAILS = {"end_point": "http://www.example.com"}


class TestRoutingRequestHandler(test_request_handler.TestRequestHandler, tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return self._build_app(routing_handler.RoutingRequestHandler)

    def test_get(self):
        self.routing.get_end_point.return_value = test_utilities.awaitable(END_POINT_DETAILS)

        response = self.fetch(test_request_handler.TestRequestHandler.build_url(), method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(END_POINT_DETAILS, json.loads(response.body))
        self.routing.get_end_point.assert_called_with(test_request_handler.ORG_CODE, test_request_handler.SERVICE_ID)

    def test_get_returns_error(self):
        self.routing.get_end_point.side_effect = Exception

        response = self.fetch(test_request_handler.TestRequestHandler.build_url(), method="GET")

        self.assertEqual(response.code, 500)
