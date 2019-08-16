import os
import pathlib
import unittest.mock

import tornado.testing
import tornado.web
import utilities.file_utilities as file_utilities
import utilities.message_utilities as message_utilities
import utilities.test_utilities as test_utilities
import utilities.xml_utilities as xml_utilities
from mhs_common.state import work_description as wd
import inbound.request.handler as handler
import mhs_common.workflow as workflow

MESSAGES_DIR = "messages"
REQUEST_FILE = "ebxml_request.msg"
EXPECTED_RESPONSE_FILE = "ebxml_ack.xml"
UNSOLICITED_REQUEST_FILE = "ebxml_unsolicited.msg"
FROM_PARTY_ID = "FROM-PARTY-ID"
CONTENT_TYPE_HEADERS = {"Content-Type": 'multipart/related; boundary="--=_MIME-Boundary"'}
REF_TO_MESSAGE_ID = "B4D38C15-4981-4366-BDE9-8F56EDC4AB72"
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'

state_data = [
    {
        wd.DATA_KEY: 'B4D38C15-4981-4366-BDE9-8F56EDC4AB72',
        wd.DATA: {
            wd.VERSION_KEY: 0,
            wd.CREATED_TIMESTAMP: '11:59',
            wd.LATEST_TIMESTAMP: '12:00',
            wd.STATUS: wd.MessageStatus.IN_OUTBOUND_WORKFLOW,
            wd.WORKFLOW: workflow.ASYNC_EXPRESS
        }
    }
]


async def state_return_values(message_key):
    """
    A method to emulate a state store returning values for a given key
    :param message_key:
    :return: data associated with that key
    """
    resposes = [data for data in state_data if data[wd.DATA_KEY] == message_key]
    if not resposes:
        return None
    else:
        return resposes[0]


class TestInboundHandler(tornado.testing.AsyncHTTPTestCase):
    """A simple integration test for the async response endpoint."""

    message_dir = pathlib.Path(__file__)/'..' / MESSAGES_DIR

    def setUp(self):
        self.state = unittest.mock.MagicMock()
        self.state.get.side_effect = state_return_values

        mock_workflow = unittest.mock.MagicMock()
        future = test_utilities.awaitable('result')
        mock_workflow.handle_inbound_message.return_value = future
        self.mocked_workflows = {
            workflow.ASYNC_EXPRESS: mock_workflow
        }

        super().setUp()

    def get_app(self):
        return tornado.web.Application([
            (r".*", handler.InboundHandler, dict(workflows=self.mocked_workflows, state_store=self.state, party_id=FROM_PARTY_ID))
        ])

    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_receive_ack(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_ack_response = file_utilities.FileUtilities.get_file_string(
            str(self.message_dir / EXPECTED_RESPONSE_FILE))
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)

    def test_post_unsolicited_message(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / UNSOLICITED_REQUEST_FILE))

        response = self.fetch("/", method="POST", body=request_body, headers=CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        message = response.body.decode('utf-8')
        self.assertEqual(
            message,
            '<html><title>500: Unknown message reference</title><body>500: Unknown message reference</body></html>')

    def test_correct_workflow(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=CONTENT_TYPE_HEADERS)
        self.mocked_workflows[workflow.ASYNC_EXPRESS].handle_inbound_message.assert_called()

        self.assertEqual(ack_response.code, 200)


class TestInboundWorkflow(tornado.testing.AsyncHTTPSTestCase):
    """A simple integration test for the async response endpoint."""

    message_dir = pathlib.Path(__file__)/'..' / MESSAGES_DIR

    def setUp(self):
        self.state = unittest.mock.MagicMock()
        self.state.get.side_effect = state_return_values
        super().setUp()

    def get_app(self):
        return tornado.web.Application([
            (r"/.*", handler.InboundHandler,
             dict(workflows=workflow.get_workflow_map(), state_store=self.state, party_id=FROM_PARTY_ID))
        ])

    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_receive_ack(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_ack_response = file_utilities.FileUtilities.get_file_string(
            str(self.message_dir / EXPECTED_RESPONSE_FILE))
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)
