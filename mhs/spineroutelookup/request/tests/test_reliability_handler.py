import json

from tornado.testing import AsyncHTTPTestCase
from utilities import test_utilities

from request import reliability_handler
from request.tests import test_request_handler

RELIABILITY_DETAILS = {"retries": 7}


class TestReliabilityRequestHandler(test_request_handler.TestRequestHandler, AsyncHTTPTestCase):
    def get_app(self):
        return self._build_app(reliability_handler.ReliabilityRequestHandler)

    def test_get(self):
        self.routing.get_reliability.return_value = test_utilities.awaitable(RELIABILITY_DETAILS)

        response = self.fetch(test_request_handler.TestRequestHandler.build_url(), method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(RELIABILITY_DETAILS, json.loads(response.body))
        self.routing.get_reliability.assert_called_with(test_request_handler.ORG_CODE, test_request_handler.SERVICE_ID)

    def test_get_returns_error(self):
        self.routing.get_reliability.side_effect = Exception

        response = self.fetch(test_request_handler.TestRequestHandler.build_url(), method="GET")

        self.assertEqual(response.code, 500)
