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
CLIENT_CERT = "client.cert"
CLIENT_KEY = "client.key"
CA_CERTS = "client.pem"
CLIENT_CERT_PATH = str(Path(CERTS_DIR) / CLIENT_CERT)
CLIENT_KEY_PATH = str(Path(CERTS_DIR) / CLIENT_KEY)
CA_CERTS_PATH = str(Path(CERTS_DIR) / CA_CERTS)
MAX_RETRIES = 3
RETRY_DELAY = 100
RETRY_DELAY_IN_SECONDS = RETRY_DELAY / 1000


class TestOutboundTransmission(TestCase):
    def setUp(self):
        self.transmission = outbound_transmission.OutboundTransmission(CERTS_DIR, CLIENT_CERT, CLIENT_KEY, CA_CERTS,
                                                                       MAX_RETRIES, RETRY_DELAY)

    @async_test
    async def test_make_request(self):
        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            sentinel.result.code = 200
            mock_fetch.return_value = awaitable(sentinel.result)

            actual_response = await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

            mock_fetch.assert_called_with(URL_VALUE,
                                          method="POST",
                                          body=MESSAGE,
                                          headers=HEADERS,
                                          client_cert=CLIENT_CERT_PATH,
                                          client_key=CLIENT_KEY_PATH,
                                          ca_certs=CA_CERTS_PATH,
                                          # ****************************************************************************
                                          # This SHOULD be true, but we must temporarily set it to false due to Opentest
                                          # limitations.
                                          # ****************************************************************************
                                          validate_cert=False
                                          )

            self.assertIs(actual_response, sentinel.result, "Expected content should be returned.")

    @async_test
    async def test_make_request_non_retriable(self):
        errors_and_expected = [
            ("HTTPClientError 400", httpclient.HTTPClientError(code=400), httpclient.HTTPClientError),
            ("SSLCertVerificationError", ssl.SSLCertVerificationError(), ssl.SSLCertVerificationError),
            ("SSLError", ssl.SSLError, ssl.SSLError)
        ]
        for description, error, expected_result in errors_and_expected:
            with self.subTest(description):
                with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
                    mock_fetch.side_effect = error

                    with self.assertRaises(expected_result):
                        await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

    @patch("asyncio.sleep")
    @async_test
    async def test_make_request_retriable(self, mock_sleep):
        mock_sleep.return_value = awaitable(None)

        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            sentinel.result.code = 200
            mock_fetch.side_effect = [httpclient.HTTPClientError(code=599), awaitable(sentinel.result)]

            actual_response = await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)

            self.assertIs(actual_response, sentinel.result, "Expected content should be returned.")
            mock_sleep.assert_called_once_with(RETRY_DELAY_IN_SECONDS)

    @patch("asyncio.sleep")
    @async_test
    async def test_make_request_max_retries(self, mock_sleep):
        mock_sleep.return_value = awaitable(None)

        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            mock_fetch.side_effect = httpclient.HTTPClientError(code=599)

            with self.assertRaises(outbound_transmission.MaxRetriesExceeded) as cm:
                await self.transmission.make_request(URL_VALUE, HEADERS, MESSAGE)
            self.assertEqual(mock_fetch.side_effect, cm.exception.__cause__)

            self.assertEqual(mock_fetch.call_count, MAX_RETRIES)
            expected_sleep_arguments = [call(RETRY_DELAY_IN_SECONDS) for i in range(MAX_RETRIES - 1)]
            self.assertEqual(expected_sleep_arguments, mock_sleep.call_args_list)

    def test_is_tornado_network_error(self):
        errors_and_expected = [("not HTTPClientError", ValueError(), False),
                               ("HTTPClientError without code 599", httpclient.HTTPClientError(code=400), False),
                               ("HTTPClientError with code 599", httpclient.HTTPClientError(code=599), True)
                               ]
        for description, error, expected_result in errors_and_expected:
            with self.subTest(description):
                result = self.transmission._is_tornado_network_error(error)

                self.assertEqual(result, expected_result)

    def test_is_retriable(self):
        errors_and_expected = [("is a tornado network error", httpclient.HTTPClientError(code=599), True),
                               ("is a HTTP error", httpclient.HTTPClientError(code=500), False),
                               ("is a not a tornado error", IOError(), True)
                               ]

        for description, error, expected_result in errors_and_expected:
            with self.subTest(description):
                result = self.transmission._is_retriable(error)

                self.assertEqual(result, expected_result)
