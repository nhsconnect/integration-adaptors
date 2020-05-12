import asyncio
import os
import pathlib
import unittest.mock

import tornado.testing
import tornado.web

import inbound.request.handler as handler
import mhs_common.workflow as workflow
import utilities.file_utilities as file_utilities
import utilities.message_utilities as message_utilities
import utilities.test_utilities as test_utilities
import utilities.xml_utilities as xml_utilities
from mhs_common.configuration import configuration_manager
from mhs_common.messages import ebxml_request_envelope
from mhs_common.state import work_description as wd
from mhs_common.workflow import asynchronous_forward_reliable as forward_reliable
from mhs_common.workflow.common import MessageData
from utilities import mdc

MESSAGES_DIR = "messages"
REQUEST_FILE = "ebxml_request"
REQUEST_FILE_UNINTENDED = "ebxml_request_unintended.msg"
REQUEST_FILE_UNKNOWN_REF_TO = "ebxml_unknown_ref_to.msg"
EXPECTED_ASYNC_ACK_RESPONSE_FILE = "ebxml_ack.xml"
EXPECTED_ASYNC_NACK_RESPONSE_FILE = "ebxml_nack.xml"
UNSOLICITED_REQUEST_FILE = "ebxml_unsolicited"
NO_REF_FILE = "ebxml_no_reference.msg"
FROM_PARTY_ID = "FROM_PARTY_ID"
ASYNC_CONTENT_TYPE_HEADERS = {"Content-Type": 'multipart/related; boundary="--=_MIME-Boundary"'}
SYNC_CONTENT_TYPE_HEADERS = {"Content-Type": 'text/xml'}
REF_TO_MESSAGE_ID = "B4D38C15-4981-4366-BDE9-8F56EDC4AB72"
UNSOLICITED_REF_TO_MESSAGE_ID = "C614484E-4B10-499A-9ACD-5D645CFACF61"
CORRELATION_ID = '10F5A436-1913-43F0-9F18-95EA0E43E61A'
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'
EXPECTED_UNSOLICITED_ATTACHMENTS = [{ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload',
                                     ebxml_request_envelope.ATTACHMENT_BASE64: False,
                                     ebxml_request_envelope.ATTACHMENT_CONTENT_ID: '8F1D7DE1-02AB-48D7-A797'
                                                                                   '-A947B09F347F@spine.nhs.uk',
                                     ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain'}]

state_data = [
    {
        wd.MESSAGE_ID: REF_TO_MESSAGE_ID,
        wd.CREATED_TIMESTAMP: '11:59',
        wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
        wd.INBOUND_STATUS: None,
        wd.WORKFLOW: workflow.ASYNC_EXPRESS
    }
]


async def state_return_values(message_key, strongly_consistent_read):
    """
    A method to emulate a state store returning values for a given key
    :param message_key:
    :return: data associated with that key
    """
    responses = [data for data in state_data if data[wd.MESSAGE_ID] == message_key]
    if not responses:
        return None
    else:
        return responses[0]


class TestInboundHandler(tornado.testing.AsyncHTTPTestCase):

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

    @unittest.mock.patch.object(message_utilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities, "get_uuid")
    def test_successful_request_has_acknowledgement_in_response(self, mock_get_uuid, mock_get_timestamp):
        """
        GIVEN an inbound message (not unsolicited)
        WHEN the message content is valid
        THEN the message is ack'ed (200) with the correct SOAP XML response
        """
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_ack_response = file_utilities.get_file_string(
            str(self.message_dir / EXPECTED_ASYNC_ACK_RESPONSE_FILE))
        request_body, ebxml = message_utilities.load_test_data(self.message_dir, REQUEST_FILE)

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.mocked_workflows[workflow.ASYNC_EXPRESS].handle_inbound_message.assert_called()
        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)
        self.mock_workflow.handle_inbound_message.assert_called_once_with(REF_TO_MESSAGE_ID, CORRELATION_ID,
                                                                          unittest.mock.ANY, MessageData(ebxml, EXPECTED_MESSAGE, []))

    def test_when_workflow_throws_exception_then_http_500_response(self):
        """
        GIVEN an inbound message (not unsolicited)
        WHEN the workflow handler raises an exception
        THEN the response is an error (500) with reason "Exception in workflow"
        """
        self.mock_workflow.handle_inbound_message.side_effect = Exception("what a failure")
        request_body, _ = message_utilities.load_test_data(self.message_dir, REQUEST_FILE)

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        self.assertEqual('500: Exception in workflow', response.body.decode())

    @unittest.mock.patch.object(mdc, "inbound_message_id")
    @unittest.mock.patch.object(mdc, "correlation_id")
    @unittest.mock.patch.object(mdc, "message_id")
    @unittest.mock.patch.object(mdc, 'interaction_id')
    def test_when_request_handled_then_logging_mdc_variables_are_set(self,
                                                                     mock_interaction_id,
                                                                     mock_message_id,
                                                                     mock_correlation_id,
                                                                     mock_inbound_message_id):
        request_body, _ = message_utilities.load_test_data(self.message_dir, REQUEST_FILE)

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)
        self.mocked_workflows[workflow.ASYNC_EXPRESS].handle_inbound_message.assert_called()

        self.assertEqual(ack_response.code, 200)
        mock_correlation_id.set.assert_called_with(CORRELATION_ID)
        mock_inbound_message_id.set.assert_called_with('C614484E-4B10-499A-9ACD-5D645CFACF61')
        mock_message_id.set.assert_called_with(REF_TO_MESSAGE_ID)
        mock_interaction_id.set.assert_called_with('MCCI_IN010000UK13')

    @unittest.mock.patch.object(message_utilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities, "get_uuid")
    def test_message_unintended_for_receiver(self, mock_get_uuid, mock_get_timestamp):
        """
        GIVEN any inbound message
        WHEN the To.PartyId is not the party id of the MHS adaptor
        THEN the message is nack'ed (200) with the correct SOAP XML response
        """
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_nack_response = file_utilities.get_file_string(
            str(self.message_dir / EXPECTED_ASYNC_NACK_RESPONSE_FILE))
        request_body = file_utilities.get_file_string(str(self.message_dir / REQUEST_FILE_UNINTENDED))

        nack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(nack_response.code, 200)
        self.assertEqual(nack_response.headers["Content-Type"], "text/xml")
        xml_utilities.XmlUtilities.assert_xml_equal(expected_nack_response, nack_response.body)
        self.mock_workflow.handle_inbound_message.assert_not_called()

    @unittest.mock.patch.object(message_utilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities, "get_uuid")
    def test_post_with_unknown_ref_to_message_id_is_rejected(self, mock_get_uuid, mock_get_timestamp):
        """
        Edge-case where an "unsolicited" forward reliable message is received that contains a RefToMessageId that we
        don't recognise. This could be caused by a message not intended for us or a problem with the state database.

        GIVEN any inbound message
        WHEN the message contains a RefToMessageId that is not recognised by the adaptor
        THEN the response is an error (500) with reason "Unknown message reference"
        """
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        request_body = file_utilities.get_file_string(str(self.message_dir / REQUEST_FILE_UNKNOWN_REF_TO))
        self.config_manager.get_interaction_details.return_value = {'workflow': workflow.FORWARD_RELIABLE}
        self.mock_forward_reliable_workflow.handle_unsolicited_inbound_message.return_value = \
            test_utilities.awaitable(None)

        nack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(nack_response.code, 500)
        self.assertIn("Unknown message reference", nack_response.body.decode())

    ###################################
    # Unsolicited inbound request tests
    ###################################

    @unittest.mock.patch.object(message_utilities, "get_timestamp")
    @unittest.mock.patch.object(message_utilities, "get_uuid")
    def test_post_unsolicited_forward_reliable_request_successfully_handled(self, mock_get_uuid, mock_get_timestamp):
        """
        GIVEN an unsolicited inbound message
        WHEN the interaction is recognised as a forward reliable workflow
        THEN the message is ack'ed (200) with the correct SOAP XML response
        AND handled with the forward reliable (unsolicited) workflow
        """
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        request_body, ebxml = message_utilities.load_test_data(self.message_dir, UNSOLICITED_REQUEST_FILE)
        self.config_manager.get_interaction_details.return_value = {'workflow': workflow.FORWARD_RELIABLE}
        self.mock_forward_reliable_workflow.handle_unsolicited_inbound_message.return_value = \
            test_utilities.awaitable(None)

        ack_response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(ack_response.code, 200)
        self.assertEqual(ack_response.headers["Content-Type"], "text/xml")
        expected_ack_response = file_utilities.get_file_string(
            str(self.message_dir / EXPECTED_ASYNC_ACK_RESPONSE_FILE))
        xml_utilities.XmlUtilities.assert_xml_equal(expected_ack_response, ack_response.body)
        self.mock_forward_reliable_workflow.handle_unsolicited_inbound_message.assert_called_once_with(
            UNSOLICITED_REF_TO_MESSAGE_ID, CORRELATION_ID, MessageData(ebxml, EXPECTED_MESSAGE, EXPECTED_UNSOLICITED_ATTACHMENTS))

    def test_post_unsolicited_non_forward_reliable_request_results_in_error_response(self):
        """
        GIVEN an unsolicited inbound message
        WHEN the interaction is not handled by a forward reliable workflow
        THEN the response is an error (500) with reason "Unsolicited messaging not supported for this interaction"
        """
        request_body, _ = message_utilities.load_test_data(self.message_dir, UNSOLICITED_REQUEST_FILE)
        self.config_manager.get_interaction_details.return_value = {'workflow': workflow.ASYNC_EXPRESS}

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        self.assertEqual('500: Unsolicited messaging not supported for this interaction', response.body.decode())


    def test_post_unsolicited_fails_if_unknown_interaction_id_in_request(self):
        """
        GIVEN an unsolicited inbound message
        WHEN the interaction is unknown
        THEN the response is an error (404) with reason "Unknown interaction ID"
        """
        request_body, _ = message_utilities.load_test_data(self.message_dir, UNSOLICITED_REQUEST_FILE)
        self.config_manager.get_interaction_details.return_value = None

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 404)
        self.assertIn('Unknown interaction ID: MCCI_IN010000UK13', response.body.decode())

    def test_post_unsolicited_fails_if_cant_determine_workflow_for_interaction_id_in_request(self):
        """
        GIVEN an unsolicited inbound message
        WHEN the interaction is mapped to an unknown workflow
        THEN the response is an error (500) with reason "Couldn't determine workflow to invoke for interaction ID"
        """
        request_body, _ = message_utilities.load_test_data(self.message_dir, UNSOLICITED_REQUEST_FILE)
        self.config_manager.get_interaction_details.return_value = {'workflow': 'invalid-workflow-name'}

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        self.assertIn("Couldn't determine workflow to invoke for interaction ID: MCCI_IN010000UK13",
                      response.body.decode())

    def test_post_unsolicited_forward_reliable_request_errors_if_workflow_errors(self):
        """
        GIVEN an unsolicited inbound message
        WHEN the workflow handler raises an exception
        THEN the response is an error (500) with reason "Exception in workflow"
        """
        request_body, _ = message_utilities.load_test_data(self.message_dir, UNSOLICITED_REQUEST_FILE)
        self.config_manager.get_interaction_details.return_value = {'workflow': workflow.FORWARD_RELIABLE}

        error_future = asyncio.Future()
        error_future.set_exception(Exception())
        self.mock_forward_reliable_workflow.handle_unsolicited_inbound_message.return_value = error_future

        response = self.fetch("/", method="POST", body=request_body, headers=ASYNC_CONTENT_TYPE_HEADERS)

        self.assertEqual(response.code, 500)
        self.assertIn("Exception in workflow", response.body.decode())
