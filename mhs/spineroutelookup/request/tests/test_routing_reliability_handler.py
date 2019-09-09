import json

import tornado.testing
import tornado.web
from utilities import test_utilities

from request import routing_reliability_handler
from request.tests import test_request_handler

END_POINT_DETAILS = {"end_point": "http://www.example.com"}
RELIABILITY_DETAILS = {"retries": 7}
COMBINED_DETAILS = {"end_point": "http://www.example.com", "retries": 7}


class TestRoutingReliabilityRequestHandler(test_request_handler
                                           .TestRequestHandler, tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return self._build_app(routing_reliability_handler.RoutingReliabilityRequestHandler)

    def test_get(self):
        self.routing.get_end_point.return_value = test_utilities.awaitable(END_POINT_DETAILS)
        self.routing.get_reliability.return_value = test_utilities.awaitable(RELIABILITY_DETAILS)

        response = self.fetch(test_request_handler.TestRequestHandler.build_url(), method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(COMBINED_DETAILS, json.loads(response.body))
        self.routing.get_end_point.assert_called_with(test_request_handler.ORG_CODE, test_request_handler.SERVICE_ID)
        self.routing.get_reliability.assert_called_with(test_request_handler.ORG_CODE, test_request_handler.SERVICE_ID)

    def test_get_returns_error(self):
        with self.subTest("Routing lookup error"):
            self.routing.get_end_point.side_effect = Exception

            response = self.fetch(test_request_handler.TestRequestHandler.build_url(), method="GET")

            self.assertEqual(response.code, 500)

        with self.subTest("Reliability lookup error"):
            self.routing.get_reliability.side_effect = Exception

            response = self.fetch(test_request_handler.TestRequestHandler.build_url(), method="GET")

            self.assertEqual(response.code, 500)
