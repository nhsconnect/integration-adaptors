import os
import pathlib
import unittest.mock

import tornado.testing
import tornado.web
import utilities.file_utilities as file_utilities
import utilities.message_utilities as message_utilities
import utilities.xml_utilities as xml_utilities

import inbound.request.handler as handler

MESSAGES_DIR = "messages"
REQUEST_FILE = "ebxml_request.msg"
EXPECTED_RESPONSE_FILE = "ebxml_ack.xml"
FROM_PARTY_ID = "FROM-PARTY-ID"
CONTENT_TYPE_HEADERS = {"Content-Type": 'multipart/related; boundary="--=_MIME-Boundary"'}
REF_TO_MESSAGE_ID = "B4D38C15-4981-4366-BDE9-8F56EDC4AB72"
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'


state_data = {


}

class TestInboundHandler(tornado.testing.AsyncHTTPTestCase):
    """A simple integration test for the async response endpoint."""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    message_dir = pathlib.Path(current_dir) / MESSAGES_DIR

    def setUp(self):
        self.state = unittest.mock.MagicMock()
        self.state.get.return_value =
        super().setUp()

    def get_app(self):
        return tornado.web.Application([
            (r".*", handler.InboundHandler, dict(state_store=self.state, party_id=FROM_PARTY_ID))
        ])

    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_post(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_ack_response = file_utilities.FileUtilities.get_file_string(
            str(self.message_dir / EXPECTED_RESPONSE_FILE))
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))
        mock_callback = unittest.mock.Mock()
        self.callbacks[REF_TO_MESSAGE_ID] = mock_callback

        ack_response = self.fetch("/", method="POST", body=request_body, headers=CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)
        mock_callback.assert_called_with(EXPECTED_MESSAGE)

    def test_post_no_callback(self):
        # If there is no callback registered for the message ID the response is in reference to, an HTTP 500 should be
        # returned.
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        response = self.fetch("/", method="POST", body=request_body, headers=CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
