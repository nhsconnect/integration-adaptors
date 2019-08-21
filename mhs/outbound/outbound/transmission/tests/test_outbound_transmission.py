from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, sentinel

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
INTERACTION_DETAILS = {
    URL_NAME: URL_VALUE,
    TYPE_NAME: TYPE_VALUE,
    CONTENT_TYPE_NAME: CONTENT_TYPE_VALUE,
    CHARSET_NAME: CHARSET_VALUE,
    SOAP_ACTION_NAME: SOAP_ACTION_VALUE,
    START_NAME: START_VALUE,
    REQUEST_TYPE_NAME: "POST"
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


class TestOutboundTransmission(TestCase):
    expected_headers = {
        "type": TYPE_VALUE,
        "Content-Type": CONTENT_TYPE_VALUE,
        "charset": CHARSET_VALUE,
        "SOAPAction": SOAP_ACTION_VALUE,
        'start': START_VALUE
    }

    def setUp(self):
        self.transmission = outbound_transmission.OutboundTransmission(CERTS_DIR, CLIENT_CERT, CLIENT_KEY, CA_CERTS,
                                                                       MAX_RETRIES)

    @async_test
    async def test_make_request(self):
        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            sentinel.result.code = 200
            mock_fetch.return_value = awaitable(sentinel.result)

            actual_response = await self.transmission.make_request(INTERACTION_DETAILS, MESSAGE)

            mock_fetch.assert_called_with(url=URL_VALUE,
                                          method="POST",
                                          body=MESSAGE,
                                          headers=self.expected_headers,
                                          client_cert=CLIENT_CERT_PATH,
                                          client_key=CLIENT_KEY_PATH,
                                          ca_certs=CA_CERTS_PATH,
                                          validate_cert=True
                                          )

            self.assertIs(actual_response, sentinel.result, "Expected content should be returned.")

    @async_test
    async def test_make_request_non_retriable(self):
        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            mock_fetch.side_effect = httpclient.HTTPClientError(code=400)

            with self.assertRaises(httpclient.HTTPClientError):
                await self.transmission.make_request(INTERACTION_DETAILS, "")

    @async_test
    async def test_make_request_retriable(self):
        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            sentinel.result.code = 200
            mock_fetch.side_effect = [httpclient.HTTPClientError(code=599), awaitable(sentinel.result)]

            actual_response = await self.transmission.make_request(INTERACTION_DETAILS, "")

            self.assertIs(actual_response, sentinel.result, "Expected content should be returned.")

    @async_test
    async def test_make_request_max_retries(self):
        with patch.object(httpclient.AsyncHTTPClient(), "fetch") as mock_fetch:
            mock_fetch.side_effect = httpclient.HTTPClientError(code=599)

            with self.assertRaises(outbound_transmission.MaxRetriesExceeded):
                await self.transmission.make_request(INTERACTION_DETAILS, "")
                self.assertEqual(mock_fetch.call_count, MAX_RETRIES)


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

    def test_build_headers(self):
        actual_headers = outbound_transmission.OutboundTransmission._build_headers({
            TYPE_NAME: TYPE_VALUE,
            CONTENT_TYPE_NAME: CONTENT_TYPE_VALUE,
            CHARSET_NAME: CHARSET_VALUE,
            SOAP_ACTION_NAME: SOAP_ACTION_VALUE,
            START_NAME: START_VALUE
        })

        self.assertEqual(self.expected_headers, actual_headers, "Headers produced should match the expected set.")

    def test_get_request_method(self):
        supported_http_methods = {"GET": "GET", "OTHER": "POST"}

        for http_method in supported_http_methods:
            with self.subTest(http_method=http_method):
                expected_request_method = supported_http_methods[http_method]

                actual_request_method = outbound_transmission.OutboundTransmission._get_request_method(
                    {"request_type": http_method})

                self.assertEqual(expected_request_method, actual_request_method,
                                 "Request method returned should match expected one.")
