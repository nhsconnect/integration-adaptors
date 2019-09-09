from unittest import TestCase
from unittest.mock import patch, Mock

from tornado import httpclient

from comms.common_https import CommonHttps
from utilities.test_utilities import async_test, awaitable

URL = "ABC.ABC"
METHOD = "GET"
HEADERS = {"a": "1"}
BODY = "hello"
CLIENT_CERT = "client.cert"
CLIENT_KEY = "client.key"
CA_CERTS = "ca.certs"


class TestCommonHttps(TestCase):

    @async_test
    async def test_make_request(self):
        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            return_value = Mock()
            mock_fetch.return_value = awaitable(return_value)

            actual_response = await CommonHttps.make_request(url=URL, method=METHOD, headers=HEADERS, body=BODY,
                                                             client_cert=CLIENT_CERT, client_key=CLIENT_KEY,
                                                             ca_certs=CA_CERTS, validate_cert=False)

            mock_fetch.assert_called_with(URL,
                                          method=METHOD,
                                          body=BODY,
                                          headers=HEADERS,
                                          client_cert=CLIENT_CERT,
                                          client_key=CLIENT_KEY,
                                          ca_certs=CA_CERTS,
                                          validate_cert=False)

            self.assertIs(actual_response, return_value, "Expected content should be returned.")

    @async_test
    async def test_make_request_defaults(self):
        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            return_value = Mock()
            mock_fetch.return_value = awaitable(return_value)

            actual_response = await CommonHttps.make_request(url=URL, method=METHOD, headers=HEADERS, body=BODY)

            mock_fetch.assert_called_with(URL,
                                          method=METHOD,
                                          body=BODY,
                                          headers=HEADERS,
                                          client_cert=None,
                                          client_key=None,
                                          ca_certs=None,
                                          validate_cert=True)

            self.assertIs(actual_response, return_value, "Expected content should be returned.")
