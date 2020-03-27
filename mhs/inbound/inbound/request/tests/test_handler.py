import asyncio
import os
import pathlib
import unittest.mock

import mhs_common.workflow as workflow
import tornado.testing
import tornado.web
import utilities.file_utilities as file_utilities
from utilities import mdc
import utilities.message_utilities as message_utilities
import utilities.test_utilities as test_utilities
import utilities.xml_utilities as xml_utilities
from mhs_common.configuration import configuration_manager
from mhs_common.messages import ebxml_request_envelope
from mhs_common.state import work_description as wd
from mhs_common.workflow import asynchronous_forward_reliable as forward_reliable

import inbound.request.handler as handler

MESSAGES_DIR = "messages"
REQUEST_FILE = "ebxml_request.msg"
REQUEST_FILE_UNINTENDED = "ebxml_request_unintended.msg"
EXPECTED_ASYNC_ACK_RESPONSE_FILE = "ebxml_ack.xml"
EXPECTED_ASYNC_NACK_RESPONSE_FILE = "ebxml_nack.xml"
UNSOLICITED_REQUEST_FILE = "ebxml_unsolicited.msg"
NO_REF_FILE = "ebxml_no_reference.msg"
FROM_PARTY_ID = "FROM_PARTY_ID"
ASYNC_CONTENT_TYPE_HEADERS = {"Content-Type": 'multipart/related; boundary="--=_MIME-Boundary"'}
SYNC_CONTENT_TYPE_HEADERS = {"Content-Type": 'text/xml'}
REF_TO_MESSAGE_ID = "B4D38C15-4981-4366-BDE9-8F56EDC4AB72"
UNSOLICITED_REF_TO_MESSAGE_ID = "B5D38C15-4981-4366-BDE9-8F56EDC4AB72"
CORRELATION_ID = '10F5A436-1913-43F0-9F18-95EA0E43E61A'
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'
EXPECTED_UNSOLICITED_ATTACHMENTS = [{ebxml_request_envelope.ATTACHMENT_BASE64: False,
                                     ebxml_request_envelope.ATTACHMENT_CONTENT_ID: '8F1D7DE1-02AB-48D7-A797'
                                                                                   '-A947B09F347F@spine.nhs.uk',
                                     ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
                                     ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload',
                                     ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Some description'}]

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

        self.mock_forward_reliable_workflow = unittest.mock.create_autospec(
            forward_reliable.AsynchronousForwardReliableWorkflow)
        self.mocked_workflows = {
            workflow.ASYNC_EXPRESS: self.mock_workflow,
            workflow.FORWARD_RELIABLE: self.mock_forward_reliable_workflow
        }
        self.config_manager = unittest.mock.create_autospec(configuration_manager.ConfigurationManager)

        super().setUp()

    def get_app(self):
        return tornado.web.Application([
            (r".*", handler.InboundHandler, dict(workflows=self.mocked_workflows,
                                                 config_manager=self.config_manager,
                                                 work_description_store=self.state, party_id=FROM_PARTY_ID))
        ])

    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_receive_ack(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_ack_response = file_utilities.FileUtilities.get_file_string(
            str(self.message_dir / EXPECTED_ASYNC_ACK_RESPONSE_FILE))
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)
        self.mock_workflow.handle_inbound_message.assert_called_once_with(REF_TO_MESSAGE_ID, CORRELATION_ID,
                                                                          unittest.mock.ANY, EXPECTED_MESSAGE)

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
        self.assertEqual('500: Exception in workflow', response.body.decode())

    def test_no_reference_to_id(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / NO_REF_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 500)

    @unittest.mock.patch.object(mdc, "inbound_message_id")
    @unittest.mock.patch.object(mdc, "correlation_id")
    @unittest.mock.patch.object(mdc, "message_id")
    @unittest.mock.patch.object(mdc, 'interaction_id')
    def test_mdc_variables_are_set(self,
                                   mock_interaction_id,
                                   mock_message_id,
                                   mock_correlation_id,
                                   mock_inbound_message_id):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE))

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)
        self.mocked_workflows[workflow.ASYNC_EXPRESS].handle_inbound_message.assert_called()

        self.assertEqual(ack_response.code, 200)
        mock_correlation_id.set.assert_called_with(CORRELATION_ID)
        mock_inbound_message_id.set.assert_called_with('C614484E-4B10-499A-9ACD-5D645CFACF61')
        mock_message_id.set.assert_called_with(REF_TO_MESSAGE_ID)
        mock_interaction_id.set.assert_called_with('MCCI_IN010000UK13')

    ###################################
    # Unsolicited inbound request tests
    ###################################

    def test_post_unsolicited_non_forward_reliable_request_results_in_error_response(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / UNSOLICITED_REQUEST_FILE))
        self.config_manager.get_interaction_details.return_value = {'workflow': workflow.ASYNC_EXPRESS}

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        self.assertEqual('500: Unknown message reference', response.body.decode())

    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_post_unsolicited_forward_reliable_request_successfully_handled(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / UNSOLICITED_REQUEST_FILE))
        self.config_manager.get_interaction_details.return_value = {'workflow': workflow.FORWARD_RELIABLE}
        self.mock_forward_reliable_workflow.handle_unsolicited_inbound_message.return_value = \
            test_utilities.awaitable(None)

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        expected_ack_response = file_utilities.FileUtilities.get_file_string(
            str(self.message_dir / EXPECTED_ASYNC_ACK_RESPONSE_FILE))
        xml_utilities.XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)
        self.mock_forward_reliable_workflow.handle_unsolicited_inbound_message.assert_called_once_with(
            UNSOLICITED_REF_TO_MESSAGE_ID, CORRELATION_ID, EXPECTED_MESSAGE, EXPECTED_UNSOLICITED_ATTACHMENTS)

    def test_post_unsolicited_fails_if_unknown_interaction_id_in_request(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / UNSOLICITED_REQUEST_FILE))
        self.config_manager.get_interaction_details.return_value = None

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 404)
        self.assertIn('Unknown interaction ID: MCCI_IN010000UK13', response.body.decode())

    def test_post_unsolicited_fails_if_cant_determine_workflow_for_interaction_id_in_request(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / UNSOLICITED_REQUEST_FILE))
        self.config_manager.get_interaction_details.return_value = {'workflow': 'invalid-workflow-name'}

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        self.assertIn("Couldn't determine workflow to invoke for interaction ID: MCCI_IN010000UK13",
                      response.body.decode())

    def test_post_unsolicited_forward_reliable_request_errors_if_workflow_errors(self):
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / UNSOLICITED_REQUEST_FILE))
        self.config_manager.get_interaction_details.return_value = {'workflow': workflow.FORWARD_RELIABLE}

        error_future = asyncio.Future()
        error_future.set_exception(Exception())
        self.mock_forward_reliable_workflow.handle_unsolicited_inbound_message.return_value = error_future

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        self.assertIn("Exception in workflow", response.body.decode())

    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_unsolicited_forward_reliable_message_unintended_for_receiver_mhs(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_nack_response = file_utilities.FileUtilities.get_file_string(
            str(self.message_dir / EXPECTED_ASYNC_NACK_RESPONSE_FILE))
        request_body = file_utilities.FileUtilities.get_file_string(str(self.message_dir / REQUEST_FILE_UNINTENDED))

        nack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(nack_response.code, 200)
        self.assertEqual(nack_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_nack_response, nack_response.body)
        self.mock_workflow.handle_inbound_message.assert_not_called()

