import unittest
from unittest import mock

from tornado import httpclient
from utilities import test_utilities

from mhs_common.routing import routing_reliability

BASE_URL = "https://example.com"
ROUTING_PATH = "routing"
RELIABILITY_PATH = "reliability"
SPINE_ORG_CODE = "SPINE ORG CODE"
CLIENT_CERT_PATH = "client/cert/path"
CLIENT_KEY_PATH = "client/key/path"
CA_CERTS_PATH = "ca/certs/path"
HTTP_PROXY_HOST = "proxy.example.com"
HTTP_PROXY_PORT = 42
HTTP_METHOD = "GET"
ORG_CODE = "ORG CODE"
SERVICE_ID = "SERVICE ID"
JSON_RESPONSE = '{"one": 1, "two": "2"}'
EXPECTED_RESPONSE = {"one": 1, "two": "2"}


class TestRoutingAndReliability(unittest.TestCase):

    def setUp(self) -> None:
        # Mock the httpclient.AsyncHTTPClient() constructor
        patcher = unittest.mock.patch.object(httpclient, "AsyncHTTPClient")
        mock_http_client_constructor = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the AsyncHTTPClient client class itself
        self.mock_http_client = unittest.mock.MagicMock()
        mock_http_client_constructor.return_value = self.mock_http_client

    @test_utilities.async_test
    async def test_should_retrieve_endpoint_details_if_given_org_code(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE)
        self._given_http_client_returns_a_json_response()

        endpoint_details = await self.routing.get_end_point(SERVICE_ID, ORG_CODE)

        self.assertEqual(EXPECTED_RESPONSE, endpoint_details)
        expected_url = self._build_url(path=ROUTING_PATH)
        self._assert_http_client_called_with_expected_args(expected_url)

    @test_utilities.async_test
    async def test_should_retrieve_endpoint_details_with_default_org_code(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE)
        self._given_http_client_returns_a_json_response()

        endpoint_details = await self.routing.get_end_point(SERVICE_ID)

        self.assertEqual(EXPECTED_RESPONSE, endpoint_details)
        expected_url = self._build_url(path=ROUTING_PATH, org_code=SPINE_ORG_CODE)
        self._assert_http_client_called_with_expected_args(expected_url)

    @test_utilities.async_test
    async def test_should_pass_through_exception_if_raised_when_retrieving_endpoint_details(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE)
        self.mock_http_client.fetch.side_effect = IOError("Something went wrong!")

        with self.assertRaises(IOError):
            await self.routing.get_end_point(SERVICE_ID, ORG_CODE)

    @test_utilities.async_test
    async def test_should_use_certificate_details_if_provided_when_retrieving_endpoint_details(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE,
                                                                 client_cert=CLIENT_CERT_PATH,
                                                                 client_key=CLIENT_KEY_PATH, ca_certs=CA_CERTS_PATH)
        self._given_http_client_returns_a_json_response()

        await self.routing.get_end_point(SERVICE_ID, ORG_CODE)

        expected_url = self._build_url(path=ROUTING_PATH)
        self._assert_http_client_called_with_expected_args(expected_url, client_cert=CLIENT_CERT_PATH,
                                                           client_key=CLIENT_KEY_PATH, ca_certs=CA_CERTS_PATH)

    @test_utilities.async_test
    async def test_should_use_proxy_if_provided_when_retrieving_endpoint_details(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE,
                                                                 http_proxy_host=HTTP_PROXY_HOST,
                                                                 http_proxy_port=HTTP_PROXY_PORT)
        self._given_http_client_returns_a_json_response()

        await self.routing.get_end_point(SERVICE_ID, ORG_CODE)

        expected_url = self._build_url(path=ROUTING_PATH)
        self._assert_http_client_called_with_expected_args(expected_url, proxy_host=HTTP_PROXY_HOST,
                                                           proxy_port=HTTP_PROXY_PORT)

    @test_utilities.async_test
    async def test_should_retrieve_reliability_details_if_given_org_code(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE)
        self._given_http_client_returns_a_json_response()

        endpoint_details = await self.routing.get_reliability(SERVICE_ID, ORG_CODE)

        self.assertEqual(EXPECTED_RESPONSE, endpoint_details)
        expected_url = self._build_url(path=RELIABILITY_PATH)
        self._assert_http_client_called_with_expected_args(expected_url)

    @test_utilities.async_test
    async def test_should_retrieve_reliability_details_with_default_org_code(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE)
        self._given_http_client_returns_a_json_response()

        endpoint_details = await self.routing.get_reliability(SERVICE_ID)

        self.assertEqual(EXPECTED_RESPONSE, endpoint_details)
        expected_url = self._build_url(path=RELIABILITY_PATH, org_code=SPINE_ORG_CODE)
        self._assert_http_client_called_with_expected_args(expected_url)

    @test_utilities.async_test
    async def test_should_pass_through_exception_if_raised_when_retrieving_reliability_details(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE)
        self.mock_http_client.fetch.side_effect = IOError("Something went wrong!")

        with self.assertRaises(IOError):
            await self.routing.get_reliability(SERVICE_ID, ORG_CODE)

    @test_utilities.async_test
    async def test_should_use_certificate_details_if_provided_when_retrieving_reliability_details(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE,
                                                                 client_cert=CLIENT_CERT_PATH,
                                                                 client_key=CLIENT_KEY_PATH, ca_certs=CA_CERTS_PATH)
        self._given_http_client_returns_a_json_response()

        await self.routing.get_reliability(SERVICE_ID, ORG_CODE)

        expected_url = self._build_url(path=RELIABILITY_PATH)
        self._assert_http_client_called_with_expected_args(expected_url, client_cert=CLIENT_CERT_PATH,
                                                           client_key=CLIENT_KEY_PATH, ca_certs=CA_CERTS_PATH)

    @test_utilities.async_test
    async def test_should_use_proxy_if_provided_when_retrieving_reliability_details(self):
        self.routing = routing_reliability.RoutingAndReliability(BASE_URL, SPINE_ORG_CODE,
                                                                 http_proxy_host=HTTP_PROXY_HOST,
                                                                 http_proxy_port=HTTP_PROXY_PORT)
        self._given_http_client_returns_a_json_response()

        await self.routing.get_reliability(SERVICE_ID, ORG_CODE)

        expected_url = self._build_url(path=RELIABILITY_PATH)
        self._assert_http_client_called_with_expected_args(expected_url, proxy_host=HTTP_PROXY_HOST,
                                                           proxy_port=HTTP_PROXY_PORT)

    def _given_http_client_returns_a_json_response(self):
        mock_response = mock.Mock()
        mock_response.body = JSON_RESPONSE
        self.mock_http_client.fetch.return_value = test_utilities.awaitable(mock_response)

    def _assert_http_client_called_with_expected_args(self, expected_url, client_cert=None, client_key=None,
                                                      ca_certs=None, proxy_host=None, proxy_port=None):
        self.mock_http_client.fetch.assert_called_with(expected_url, raise_error=True,
                                                       method=HTTP_METHOD, body=None, headers=None,
                                                       client_cert=client_cert, client_key=client_key,
                                                       ca_certs=ca_certs, validate_cert=True, proxy_host=proxy_host,
                                                       proxy_port=proxy_port)

    @staticmethod
    def _build_url(path: str, org_code: str = ORG_CODE) -> str:
        return BASE_URL + "/" + path + "?org-code=" + org_code + "&service-id=" + SERVICE_ID
