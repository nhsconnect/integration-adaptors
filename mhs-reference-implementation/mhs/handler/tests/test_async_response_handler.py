import os
from pathlib import Path
from unittest.mock import Mock, patch

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from mhs.builder.ebxml_ack_message_builder import EbXmlAckMessageBuilder
from mhs.handler.async_response_handler import AsyncResponseHandler
from mhs.parser.ebxml_message_parser import EbXmlRequestMessageParser
from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities
from utilities.xml_utilities import XmlUtilities

MESSAGES_DIR = "messages"
REQUEST_FILE = "ebxml_request.msg"
EXPECTED_RESPONSE_FILE = "ebxml_ack.xml"
FROM_PARTY_ID = "FROM-PARTY-ID"
CONTENT_TYPE_HEADERS = {"Content-Type": 'multipart/related; boundary="--=_MIME-Boundary"'}
REF_TO_MESSAGE_ID = "B4D38C15-4981-4366-BDE9-8F56EDC4AB72"
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'


class TestAsyncResponseHandler(AsyncHTTPTestCase):
    """A simple integration test for the async response endpoint."""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    message_dir = Path(current_dir) / MESSAGES_DIR

    def setUp(self):
        self.callbacks = {}
        super().setUp()

    def get_app(self):
        ack_builder = EbXmlAckMessageBuilder()
        message_parser = EbXmlRequestMessageParser()
        return Application([
            (r".*", AsyncResponseHandler,
             dict(ack_builder=ack_builder, message_parser=message_parser, callbacks=self.callbacks,
                  party_id=FROM_PARTY_ID))
        ])

    @patch.object(MessageUtilities, "get_timestamp")
    @patch.object(MessageUtilities, "get_uuid")
    def test_post(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_ack_response = FileUtilities.get_file_string(str(self.message_dir / EXPECTED_RESPONSE_FILE))
        request_body = FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))
        mock_callback = Mock()
        self.callbacks[REF_TO_MESSAGE_ID] = mock_callback

        ack_response = self.fetch("/", method="POST", body=request_body, headers=CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)
        mock_callback.assert_called_with(EXPECTED_MESSAGE)

    def test_post_no_callback(self):
        # If there is no callback registered for the message ID the response is in reference to, an HTTP 500 should be
        # returned.
        request_body = FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        response = self.fetch("/", method="POST", body=request_body, headers=CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
