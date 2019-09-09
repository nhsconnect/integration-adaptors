import json
import unittest
from unittest import mock

from utilities import test_utilities

from mhs_common.routing import routing_reliability

BASE_URL = "https://example.com"
SPINE_ORG_CODE = "SPINE ORG CODE"
HTTP_METHOD = "GET"
ORG_CODE = "ORG CODE"
SERVICE_ID = "SERVICE ID"
RESPONSE = {"one": 1, "two": "2"}


@mock.patch("comms.common_https.CommonHttps")
class TestRoutingAndReliability(unittest.TestCase):

    def setUp(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE)

    @test_utilities.async_test
    async def test_get_end_point(self, mock_https):
        mock_response = mock.Mock()
        mock_response.body = json.dumps(RESPONSE)
        mock_https.make_request.return_value = test_utilities.awaitable(mock_response)

        endpoint_details = await self.routing.get_end_point(SERVICE_ID, ORG_CODE)

        self.assertEqual(RESPONSE, endpoint_details)
        expected_url = self._build_url(path="routing")
        mock_https.make_request.assert_called_with(url=expected_url, method=HTTP_METHOD, headers=None, body=None)

    @test_utilities.async_test
    async def test_get_end_point_default_org_code(self, mock_https):
        mock_response = mock.Mock()
        mock_response.body = json.dumps(RESPONSE)
        mock_https.make_request.return_value = test_utilities.awaitable(mock_response)

        endpoint_details = await self.routing.get_end_point(SERVICE_ID)

        self.assertEqual(RESPONSE, endpoint_details)
        expected_url = self._build_url(path="routing", org_code=SPINE_ORG_CODE)
        mock_https.make_request.assert_called_with(url=expected_url, method=HTTP_METHOD, headers=None, body=None)

    @test_utilities.async_test
    async def test_get_end_point_handles_exception(self, mock_https):
        mock_https.make_request.side_effect = IOError("Something went wrong!")

        with self.assertRaises(IOError):
            await self.routing.get_end_point(SERVICE_ID, ORG_CODE)

    @test_utilities.async_test
    async def test_get_reliability(self, mock_https):
        mock_response = mock.Mock()
        mock_response.body = json.dumps(RESPONSE)
        mock_https.make_request.return_value = test_utilities.awaitable(mock_response)

        endpoint_details = await self.routing.get_reliability(SERVICE_ID, ORG_CODE)

        self.assertEqual(RESPONSE, endpoint_details)
        expected_url = self._build_url(path="reliability")
        mock_https.make_request.assert_called_with(url=expected_url, method=HTTP_METHOD, headers=None, body=None)

    @test_utilities.async_test
    async def test_get_reliability_default_org_code(self, mock_https):
        mock_response = mock.Mock()
        mock_response.body = json.dumps(RESPONSE)
        mock_https.make_request.return_value = test_utilities.awaitable(mock_response)

        endpoint_details = await self.routing.get_reliability(SERVICE_ID)

        self.assertEqual(RESPONSE, endpoint_details)
        expected_url = self._build_url(path="reliability", org_code=SPINE_ORG_CODE)
        mock_https.make_request.assert_called_with(url=expected_url, method=HTTP_METHOD, headers=None, body=None)

    @test_utilities.async_test
    async def test_get_reliability_handles_exception(self, mock_https):
        mock_https.make_request.side_effect = IOError("Something went wrong!")

        with self.assertRaises(IOError):
            await self.routing.get_reliability(SERVICE_ID, ORG_CODE)

    @staticmethod
    def _build_url(path: str, org_code: str = ORG_CODE) -> str:
        return BASE_URL + "/" + path + "?org-code=" + org_code + "&service-id=" + SERVICE_ID
