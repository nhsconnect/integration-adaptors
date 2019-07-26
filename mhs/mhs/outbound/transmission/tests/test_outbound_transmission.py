from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, sentinel, Mock

import requests

import mhs.outbound.transmission.outbound_transmission as outbound_transmission

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

MESSAGE = "message"

CERTS_DIR = "certs_dir"
CLIENT_CERT_PATH = str(Path(CERTS_DIR) / "client.cert")
CLIENT_KEY_PATH = str(Path(CERTS_DIR) / "client.key")
CLIENT_PEM_PATH = str(Path(CERTS_DIR) / "client.pem")


class TestOutboundTransmission(TestCase):
    expected_headers = {
        "type": TYPE_VALUE,
        "Content-Type": CONTENT_TYPE_VALUE,
        "charset": CHARSET_VALUE,
        "SOAPAction": SOAP_ACTION_VALUE,
        'start': START_VALUE
    }

    def setUp(self):
        self.transmission = outbound_transmission.OutboundTransmission(CERTS_DIR)

    @patch("requests.post")
    def test_make_request(self, mock_post):
        mock_result = Mock()
        mock_result.content = sentinel.content
        mock_post.return_value = mock_result

        interaction_details = {
            URL_NAME: URL_VALUE,
            TYPE_NAME: TYPE_VALUE,
            CONTENT_TYPE_NAME: CONTENT_TYPE_VALUE,
            CHARSET_NAME: CHARSET_VALUE,
            SOAP_ACTION_NAME: SOAP_ACTION_VALUE,
            START_NAME: START_VALUE,
            REQUEST_TYPE_NAME: "POST"
        }

        actual_response = self.transmission.make_request(interaction_details, MESSAGE)

        mock_post.assert_called_with(URL_VALUE,
                                     data=MESSAGE,
                                     headers=self.expected_headers,
                                     cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
                                     verify=CLIENT_PEM_PATH
                                     )
        mock_result.raise_for_status.assert_called()
        self.assertIs(actual_response, sentinel.content, "Expected content should be returned.")

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
        supported_http_methods = {"GET": requests.get, "OTHER": requests.post}

        for http_method in supported_http_methods:
            with self.subTest(http_method=http_method):
                expected_request_method = supported_http_methods[http_method]

                actual_request_method = outbound_transmission.OutboundTransmission._get_request_method(
                    {"request_type": http_method})

                self.assertEqual(expected_request_method, actual_request_method,
                                 "Request method returned should match expected one.")
