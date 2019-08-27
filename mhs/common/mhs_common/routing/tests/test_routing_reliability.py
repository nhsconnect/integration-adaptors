import json
import unittest
from unittest import mock

from utilities import test_utilities

from mhs_common.routing import routing_reliability

BASE_URL = "https://example.com"
HTTP_METHOD = "GET"
ORG_CODE = "ORG CODE"
SERVICE_ID = "SERVICE ID"
RESPONSE = {"one": 1, "two": "2"}


@mock.patch("comms.common_https.CommonHttps")
class TestRoutingAndReliability(unittest.TestCase):

    def setUp(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL)

    @test_utilities.async_test
    async def test_get_end_point(self, mock_https):
        mock_response = mock.Mock()
        mock_response.body = json.dumps(RESPONSE)
        mock_https.make_request.return_value = test_utilities.awaitable(mock_response)

        endpoint_details = await self.routing.get_end_point(ORG_CODE, SERVICE_ID)

        self.assertEqual(RESPONSE, endpoint_details)
        expected_url = self._build_url(path="routing")
        mock_https.make_request.assert_called_with(url=expected_url, method=HTTP_METHOD, headers=None, body=None)

    @test_utilities.async_test
    async def test_get_end_point_handles_exception(self, mock_https):
        mock_https.make_request.side_effect = IOError("Something went wrong!")

        with self.assertRaises(IOError):
            await self.routing.get_end_point(ORG_CODE, SERVICE_ID)

    @test_utilities.async_test
    async def test_get_reliability(self, mock_https):
        mock_response = mock.Mock()
        mock_response.body = json.dumps(RESPONSE)
        mock_https.make_request.return_value = test_utilities.awaitable(mock_response)

        endpoint_details = await self.routing.get_reliability(ORG_CODE, SERVICE_ID)

        self.assertEqual(RESPONSE, endpoint_details)
        expected_url = self._build_url(path="reliability")
        mock_https.make_request.assert_called_with(url=expected_url, method=HTTP_METHOD, headers=None, body=None)

    @test_utilities.async_test
    async def test_get_reliability_handles_exception(self, mock_https):
        mock_https.make_request.side_effect = IOError("Something went wrong!")

        with self.assertRaises(IOError):
            await self.routing.get_reliability(ORG_CODE, SERVICE_ID)

    @staticmethod
    def _build_url(path: str) -> str:
        return BASE_URL + "/" + path + "?org-code=" + ORG_CODE + "&service-id=" + SERVICE_ID
