import json
import unittest.mock

import tornado.web
from tornado.testing import AsyncHTTPTestCase
from utilities import test_utilities

from request import reliability_handler
from request.tests import test_request_handler

RELIABILITY_DETAILS = {"retries": 7}


class TestReliabilityRequestHandler(AsyncHTTPTestCase):
    def get_app(self):
        self.routing = unittest.mock.Mock()

        return tornado.web.Application([
            (r"/", reliability_handler.ReliabilityRequestHandler, {"routing": self.routing})
        ])

    def test_get(self):
        self.routing.get_reliability.return_value = test_utilities.awaitable(RELIABILITY_DETAILS)

        response = self.fetch(test_request_handler.build_url(), method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(RELIABILITY_DETAILS, json.loads(response.body))
        self.routing.get_reliability.assert_called_with(test_request_handler.ORG_CODE, test_request_handler.SERVICE_ID)

    def test_get_returns_error(self):
        self.routing.get_reliability.side_effect = Exception

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
