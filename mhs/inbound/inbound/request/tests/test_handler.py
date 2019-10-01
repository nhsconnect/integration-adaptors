import os
import pathlib
import unittest.mock
from unittest import skip

import mhs_common.workflow as workflow
import tornado.testing
import tornado.web
import utilities.file_utilities as file_utilities
import utilities.integration_adaptors_logger as log
import utilities.message_utilities as message_utilities
import utilities.test_utilities as test_utilities
import utilities.xml_utilities as xml_utilities
import inbound.request.handler as handler

from mhs_common.state import work_description as wd

MESSAGES_DIR = "messages"
REQUEST_FILE = "ebxml_request.msg"
EXPECTED_ASYNC_RESPONSE_FILE = "ebxml_ack.xml"
EXPECTED_SYNC_RESPONSE_FILE = "sync_message.xml"
UNSOLICITED_REQUEST_FILE = "ebxml_unsolicited.msg"
NO_REF_FILE = "ebxml_no_reference.msg"
FROM_PARTY_ID = "FROM-PARTY-ID"
ASYNC_CONTENT_TYPE_HEADERS = {"Content-Type": 'multipart/related; boundary="--=_MIME-Boundary"'}
SYNC_CONTENT_TYPE_HEADERS = {"Content-Type": 'text/xml'}
REF_TO_MESSAGE_ID = "B4D38C15-4981-4366-BDE9-8F56EDC4AB72"
CORRELATION_ID = '10F5A436-1913-43F0-9F18-95EA0E43E61A'
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'

state_data = [
    {
        wd.DATA_KEY: REF_TO_MESSAGE_ID,
        wd.DATA: {
            wd.VERSION_KEY: 0,
            wd.CREATED_TIMESTAMP: '11:59',
            wd.LATEST_TIMESTAMP: '12:00',
            wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
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

    current_dir = os.path.dirname(os.path.abspath(__file__))
    message_dir = pathlib.Path(current_dir) / MESSAGES_DIR

    def setUp(self):
        self.state = unittest.mock.MagicMock()
        self.state.get.side_effect = state_return_values

        self.mock_workflow = unittest.mock.MagicMock()
        self.mock_workflow.handle_inbound_message.return_value = test_utilities.awaitable(None)
        self.mocked_workflows = {
            workflow.ASYNC_EXPRESS: self.mock_workflow
        }

        super().setUp()

    def get_app(self):
        return tornado.web.Application([
            (r".*", handler.InboundHandler, dict(workflows=self.mocked_workflows,
                                                 work_description_store=self.state, party_id=FROM_PARTY_ID))
        ])

    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_receive_ack(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_ack_response = file_utilities.FileUtilities.get_file_string(
            str(self.message_dir / EXPECTED_ASYNC_RESPONSE_FILE))
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)
        self.mock_workflow.handle_inbound_message.assert_called_once_with(REF_TO_MESSAGE_ID, CORRELATION_ID, unittest.mock.ANY, EXPECTED_MESSAGE)

    def test_post_unsolicited_message(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / UNSOLICITED_REQUEST_FILE))

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        message = response.body.decode('utf-8')
        self.assertEqual(
            message,
            '<html><title>500: Unknown message reference</title><body>500: Unknown message reference</body></html>')

    def test_correct_workflow(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)
        self.mocked_workflows[workflow.ASYNC_EXPRESS].handle_inbound_message.assert_called()

        self.assertEqual(ack_response.code, 200)

    def test_workflow_throws_exception(self):
        self.mock_workflow.handle_inbound_message.side_effect = Exception("what a failure")
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        expected = '<html><title>500: Exception in workflow</title><body>500: Exception in workflow</body></html>'
        self.assertEqual(response.body.decode('utf-8'), expected)

    def test_no_reference_to_id(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / NO_REF_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 500)

    @unittest.mock.patch.object(log, "inbound_message_id")
    @unittest.mock.patch.object(log, "correlation_id")
    @unittest.mock.patch.object(log, "message_id")
    @unittest.mock.patch.object(log, 'interaction_id')
    def test_logging_context_variables_are_set(self,
                                               mock_interaction_id,
                                               mock_message_id,
                                               mock_correlation_id,
                                               mock_inbound_message_id):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)
        self.mocked_workflows[workflow.ASYNC_EXPRESS].handle_inbound_message.assert_called()

        self.assertEqual(ack_response.code, 200)
        mock_correlation_id.set.assert_called_with(CORRELATION_ID)
        log.inbound_message_id.set.assert_called_with('C614484E-4B10-499A-9ACD-5D645CFACF61')
        mock_message_id.set.assert_called_with(REF_TO_MESSAGE_ID)
        mock_interaction_id.set.assert_called_with('MCCI_IN010000UK13')

    @skip('Unskip once sync workflow works')
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_receive_sync_message(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_sync_response = file_utilities.FileUtilities.get_file_string(
            str(self.message_dir / EXPECTED_SYNC_RESPONSE_FILE))
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        sync_response = self.fetch("/", method="POST", body=request_body, headers=SYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(sync_response.code, 200)
        self.assertEqual(sync_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_sync_response, sync_response.body)
        self.mock_workflow.handle_inbound_message.assert_called_once_with(REF_TO_MESSAGE_ID, CORRELATION_ID,
                                                                          unittest.mock.ANY, EXPECTED_MESSAGE)

