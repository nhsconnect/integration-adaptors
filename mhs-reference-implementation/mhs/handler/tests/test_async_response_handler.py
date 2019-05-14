import os
from pathlib import Path
from unittest.mock import patch

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from mhs.builder.ebxml_ack_message_builder import EbXmlAckMessageBuilder
from mhs.parser.ebxml_message_parser import EbXmlRequestMessageParser
from mhs.handler.async_response_handler import AsyncResponseHandler
from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities
from utilities.xml_utilities import XmlUtilities

MESSAGES_DIR = "messages"
REQUEST_FILE = "ebxml_request.msg"
EXPECTED_RESPONSE_FILE = "ebxml_ack.xml"


class TestAsyncResponseHandler(AsyncHTTPTestCase):
    """A simple integration test for the async response endpoint."""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    message_dir = Path(current_dir) / MESSAGES_DIR

    def get_app(self):
        ack_builder = EbXmlAckMessageBuilder()
        message_parser = EbXmlRequestMessageParser()
        return Application([
            (r".*", AsyncResponseHandler, dict(ack_builder=ack_builder, message_parser=message_parser))
        ])

    @patch.object(MessageUtilities, "get_timestamp")
    @patch.object(MessageUtilities, "get_uuid")
    def test_post(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_response = FileUtilities.get_file_string(str(self.message_dir / EXPECTED_RESPONSE_FILE))
        request_body = FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        headers = {"Content-Type": 'multipart/related; boundary="--=_MIME-Boundary"'}
        response = self.fetch("/", method="POST", body=request_body, headers=headers)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/xml")
        XmlUtilities.assert_xml_equal(expected_response, response.body)
