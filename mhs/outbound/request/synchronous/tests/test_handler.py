import unittest.mock
from unittest.mock import patch
import tornado.testing
import tornado.web
import request.synchronous.handler as handler
from utilities import integration_adaptors_logger as log, test_utilities
from utilities import message_utilities


MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
MOCK_UUID_2 = "82B5FE90-FD7C-41AC-82A3-9032FB0317FB"
INTERACTION_NAME = "interaction"
REQUEST_BODY = "A request"
WORKFLOW_NAME = "workflow name"
INTERACTION_DETAILS = {'workflow': WORKFLOW_NAME}


class TestSynchronousHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        self.workflow = unittest.mock.Mock()
        self.config_manager = unittest.mock.Mock()
        return tornado.web.Application([
            (r"/", handler.SynchronousHandler,
             dict(config_manager=self.config_manager, workflows={WORKFLOW_NAME: self.workflow}))
        ])

    def tearDown(self):
        log.message_id.set(None)
        log.correlation_id.set(None)

    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    @patch.object(log, "correlation_id")
    @patch.object(log, "message_id")
    def test_post_message(self, mock_message_id, mock_correlation_id, mock_get_uuid):
        expected_response = "Hello world!"
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, expected_response))
        mock_get_uuid.side_effect = [MOCK_UUID, MOCK_UUID_2]
        self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME}, body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/xml")
        self.assertEqual(response.body.decode(), expected_response)

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_called_with(MOCK_UUID, INTERACTION_DETAILS, REQUEST_BODY)

        mock_message_id.set.assert_called_with(MOCK_UUID)
        mock_correlation_id.set.assert_called_with(MOCK_UUID_2)

    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    @patch.object(log, "correlation_id")
    @patch.object(log, "message_id")
    def test_post_message_with_message_id_passed_in(self, mock_message_id, mock_correlation_id, mock_get_uuid):
        message_id = "message-id"
        expected_response = "Hello world!"
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, expected_response))
        mock_get_uuid.return_value = MOCK_UUID
        self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

        response = self.fetch("/", method="POST",
                              headers={"Interaction-Id": INTERACTION_NAME, "Message-Id": message_id}, body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        mock_get_uuid.assert_called_once()

        self.workflow.handle_outbound_message.assert_called_with(message_id, INTERACTION_DETAILS, REQUEST_BODY)

        mock_message_id.set.assert_called_with(message_id)
        mock_correlation_id.set.assert_called_with(MOCK_UUID)

    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    @patch.object(log, "correlation_id")
    @patch.object(log, "message_id")
    def test_post_message_with_correlation_id_passed_in(self, mock_message_id, mock_correlation_id, mock_get_uuid):
        correlation_id = "correlation-id"
        expected_response = "Hello world!"
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, expected_response))
        mock_get_uuid.return_value = MOCK_UUID
        self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

        response = self.fetch("/", method="POST",
                              headers={"Interaction-Id": INTERACTION_NAME, "Correlation-Id": correlation_id},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        mock_get_uuid.assert_called_once()

        self.workflow.handle_outbound_message.assert_called_with(MOCK_UUID, INTERACTION_DETAILS, REQUEST_BODY)

        mock_message_id.set.assert_called_with(MOCK_UUID)
        mock_correlation_id.set.assert_called_with(correlation_id)

    def test_post_message_where_workflow_not_found_on_interaction_details(self):
        self.config_manager.get_interaction_details.return_value = {}

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME}, body=REQUEST_BODY)

        self.assertEqual(response.code, 500)
        self.assertIn(f"Couldn't determine workflow to invoke for interaction ID: {INTERACTION_NAME}",
                      response.body.decode())

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_not_called()

    def test_post_message_where_interaction_detail_has_invalid_workflow(self):
        self.config_manager.get_interaction_details.return_value = {'workflow': 'nonexistent workflow'}

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME}, body=REQUEST_BODY)

        self.assertEqual(response.code, 500)
        self.assertIn(f"Couldn't determine workflow to invoke for interaction ID: {INTERACTION_NAME}",
                      response.body.decode())

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_not_called()

    def test_post_with_no_interaction_name(self):
        response = self.fetch("/", method="POST", body="A request")

        self.assertEqual(response.code, 404)
        self.assertIn('Required Interaction-Id header not found', response.body.decode())

    def test_post_with_invalid_interaction_name(self):
        self.config_manager.get_interaction_details.return_value = None

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME}, body="A request")

        self.assertEqual(response.code, 404)
        self.assertIn(f'Unknown interaction ID: {INTERACTION_NAME}', response.body.decode())

    def test_post_with_no_body(self):
        self.config_manager.get_interaction_details.return_value = None

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME}, body="")

        self.assertEqual(response.code, 400)
        self.assertIn("Body missing from request", response.body.decode())
