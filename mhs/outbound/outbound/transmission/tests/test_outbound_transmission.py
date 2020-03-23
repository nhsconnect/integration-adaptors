import ssl
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, sentinel, call

import definitions
from tornado import httpclient
from utilities.test_utilities import async_test, awaitable

from outbound.transmission import outbound_transmission

URL_NAME = "url"
URL_VALUE = "URL"
TYPE_NAME = "type"
TYPE_VALUE = "TYPE"
CONTENT_TYPE_NAME = "content_type"
CONTENT_TYPE_VALUE = "CONTENT_TYPE"
CHARSET_NAME = "charset"
CHARSET_VALUE = "CHARSET"
SOAP_ACTION_NAME = "soap_action"
SOAP_ACTION_VALUE = "SOAP_ACTION"
START_VALUE = "START"
START_NAME = "start"
REQUEST_TYPE_NAME = "request_type"
HEADERS = {
    "type": TYPE_VALUE,
    "Content-Type": CONTENT_TYPE_VALUE,
    "charset": CHARSET_VALUE,
    "SOAPAction": SOAP_ACTION_VALUE,
    'start': START_VALUE
}
MESSAGE = "message"

CERTS_DIR = str(Path(definitions.ROOT_DIR) / "data/certs_dir")
CLIENT_CERT_PATH = str(Path(CERTS_DIR) / "client.cert")
CLIENT_KEY_PATH = str(Path(CERTS_DIR) / "client.key")
CA_CERTS_PATH = str(Path(CERTS_DIR) / "client.pem")
MAX_RETRIES = 3
EXPECTED_MAX_HTTP_REQUESTS = MAX_RETRIES + 1
RETRY_DELAY = 100
RETRY_DELAY_IN_SECONDS = RETRY_DELAY / 1000
VALIDATE_CERT = True
HTTP_PROXY_HOST = "proxy_host"
HTTP_PROXY_PORT = 3128


class TestOutboundTransmission(TestCase):
    def setUp(self):
        self.transmission = outbound_transmission.OutboundTransmission(CLIENT_CERT_PATH, CLIENT_KEY_PATH, CA_CERTS_PATH,
                                                                       MAX_RETRIES, RETRY_DELAY, VALIDATE_CERT)

    @async_test
    async def test_should_make_HTTP_request_with_default_parameters(self):
        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            sentinel.result.code = 200
            mock_fetch.return_value = awaitable(sentinel.result)

            actual_response = await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

            mock_fetch.assert_called_with(URL_VALUE,
                                          method="POST",
                                          raise_error=True,
                                          body=MESSAGE,
                                          headers=HEADERS,
                                          client_cert=CLIENT_CERT_PATH,
                                          client_key=CLIENT_KEY_PATH,
                                          ca_certs=CA_CERTS_PATH,
                                          validate_cert=VALIDATE_CERT,
                                          proxy_host=None,
                                          proxy_port=None
                                          )

            self.assertIs(actual_response, sentinel.result, "Expected content should be returned.")

    @async_test
    async def test_should_use_proxy_details_if_provided(self):
        self.transmission = outbound_transmission.OutboundTransmission(CLIENT_CERT_PATH, CLIENT_KEY_PATH, CA_CERTS_PATH,
                                                                       MAX_RETRIES, RETRY_DELAY, VALIDATE_CERT, HTTP_PROXY_HOST,
                                                                       HTTP_PROXY_PORT)

        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            sentinel.result.code = 200
            mock_fetch.return_value = awaitable(sentinel.result)

            actual_response = await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

            mock_fetch.assert_called_with(URL_VALUE,
                                          method="POST",
                                          raise_error=True,
                                          body=MESSAGE,
                                          headers=HEADERS,
                                          client_cert=CLIENT_CERT_PATH,
                                          client_key=CLIENT_KEY_PATH,
                                          ca_certs=CA_CERTS_PATH,
                                          validate_cert=VALIDATE_CERT,
                                          proxy_host=HTTP_PROXY_HOST,
                                          proxy_port=HTTP_PROXY_PORT)

            self.assertIs(actual_response, sentinel.result, "Expected content should be returned.")

    @async_test
    async def test_should_not_retry_request_if_non_retriable_exception_raised(self):
        test_cases = [
            ("HTTPClientError 400", httpclient.HTTPClientError(code=400), httpclient.HTTPClientError),
            ("SSLError", ssl.SSLError, ssl.SSLError)
        ]
        for description, error, expected_result in test_cases:
            with self.subTest(description):
                with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
                    mock_fetch.side_effect = error

                    with self.assertRaises(expected_result):
                        await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

    @async_test
    async def test_should_retry_request_if_retriable_exception_raised(self):
        test_cases = [
            ("HTTPClientError 599", httpclient.HTTPClientError(code=599)),
            ("Generic Exception", Exception)
        ]

        for description, error in test_cases:
            with self.subTest(description):
                with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
                    sentinel.result.code = 200
                    mock_fetch.side_effect = [error, awaitable(sentinel.result)]

                    actual_response = await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

                    self.assertIs(actual_response, sentinel.result, "Expected content should be returned.")

    @patch("asyncio.sleep")
    @async_test
    async def test_should_try_request_twice_if_max_retries_set_to_one(self, mock_sleep):
        transmission = outbound_transmission.OutboundTransmission(CLIENT_CERT_PATH, CLIENT_KEY_PATH, CA_CERTS_PATH, 1,
                                                                  RETRY_DELAY, VALIDATE_CERT)
        mock_sleep.return_value = awaitable(None)

        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            mock_fetch.side_effect = Exception

            with self.assertRaises(Exception):
                await transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

            self.assertEqual(mock_fetch.call_count, 2)

    @patch("asyncio.sleep")
    @async_test
    async def test_should_retry_request_up_to_configured_max_retries(self, mock_sleep):
        mock_sleep.return_value = awaitable(None)

        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            exception_raised = Exception
            mock_fetch.side_effect = exception_raised

            with self.assertRaises(exception_raised):
                await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

            self.assertEqual(mock_fetch.call_count, EXPECTED_MAX_HTTP_REQUESTS)
            expected_sleep_arguments = [call(RETRY_DELAY_IN_SECONDS) for _ in range(MAX_RETRIES)]
            self.assertEqual(expected_sleep_arguments, mock_sleep.call_args_list)
