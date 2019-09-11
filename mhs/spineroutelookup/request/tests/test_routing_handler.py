import json
import unittest.mock

import tornado.testing
import tornado.web
from utilities import test_utilities

from request import routing_handler
from request.tests import test_request_handler

END_POINT_DETAILS = {"end_point": "http://www.example.com"}


class TestRoutingRequestHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        self.routing = unittest.mock.Mock()

        return tornado.web.Application([
            (r"/", routing_handler.RoutingRequestHandler, {"routing": self.routing})
        ])

    def test_get(self):
        self.routing.get_end_point.return_value = test_utilities.awaitable(END_POINT_DETAILS)

        response = self.fetch(test_request_handler.build_url(), method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(END_POINT_DETAILS, json.loads(response.body))
        self.routing.get_end_point.assert_called_with(test_request_handler.ORG_CODE, test_request_handler.SERVICE_ID)

    def test_get_returns_error(self):
        self.routing.get_end_point.side_effect = Exception

        response = self.fetch(test_request_handler.build_url(), method="GET")

        self.assertEqual(response.code, 500)

    def test_get_handles_missing_params(self):
        with self.subTest("Missing Org Code"):
            response = self.fetch(
                test_request_handler.build_url(org_code=None, service_id=test_request_handler.SERVICE_ID), method="GET")

            self.assertEqual(response.code, 400)

        with self.subTest("Missing Service ID"):
            response = self.fetch(
                test_request_handler.build_url(org_code=test_request_handler.ORG_CODE, service_id=None), method="GET")

            self.assertEqual(response.code, 400)

        with self.subTest("Missing Org Code & Service ID"):
            response = self.fetch(test_request_handler.build_url(org_code=None, service_id=None), method="GET")

            self.assertEqual(response.code, 400)
