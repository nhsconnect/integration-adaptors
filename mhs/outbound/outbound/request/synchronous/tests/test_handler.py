import unittest.mock
from unittest.mock import patch

import tornado.testing
import tornado.web
import tornado.util
from utilities import integration_adaptors_logger as log, test_utilities
from utilities import message_utilities
import mhs_common.state.work_description as wd
from outbound.request.synchronous import handler

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
MOCK_UUID_2 = "82B5FE90-FD7C-41AC-82A3-9032FB0317FB"
INTERACTION_NAME = "interaction"
REQUEST_BODY = "A request"
WORKFLOW_NAME = "workflow name"

INTERACTION_DETAILS = {'workflow': WORKFLOW_NAME, 'sync-async': 'true'}
SYNC_ASYNC_WORKFLOW = "sync-async"


class TestSynchronousHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        self.workflow = unittest.mock.Mock()
        self.sync_async_workflow = unittest.mock.MagicMock()
        self.config_manager = unittest.mock.Mock()
        return tornado.web.Application([
            (r"/", handler.SynchronousHandler,
             dict(config_manager=self.config_manager, workflows={WORKFLOW_NAME: self.workflow,
                                                                 SYNC_ASYNC_WORKFLOW: self.sync_async_workflow}))
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

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'false'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/xml")
        self.assertEqual(response.body.decode(), expected_response)

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_called_with(MOCK_UUID, MOCK_UUID_2, INTERACTION_DETAILS,
                                                                 REQUEST_BODY, None)

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
                              headers={"Interaction-Id": INTERACTION_NAME, "Message-Id": message_id,
                                       'sync-async': 'false'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        mock_get_uuid.assert_called_once()

        self.workflow.handle_outbound_message.assert_called_with(message_id, MOCK_UUID, INTERACTION_DETAILS,
                                                                 REQUEST_BODY, None)

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
                              headers={"Interaction-Id": INTERACTION_NAME, "Correlation-Id": correlation_id,
                                       'sync-async': 'false'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        mock_get_uuid.assert_called_once()

        self.workflow.handle_outbound_message.assert_called_with(MOCK_UUID, correlation_id, INTERACTION_DETAILS,
                                                                 REQUEST_BODY, None)

        mock_message_id.set.assert_called_with(MOCK_UUID)
        mock_correlation_id.set.assert_called_with(correlation_id)

    def test_post_message_where_workflow_returns_error_response(self):
        for http_status in [400, 409, 500, 503]:
            with self.subTest(http_status=http_status):
                expected_response = "Error response body"
                self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((http_status,
                                                                                               expected_response))
                self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

                response = self.fetch("/", method="POST",
                                      headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'false'},
                                      body=REQUEST_BODY)

                self.assertEqual(response.code, http_status)
                self.assertEqual(response.headers["Content-Type"], "text/plain")
                self.assertEqual(response.body.decode(), expected_response)

    def test_post_message_where_workflow_not_found_on_interaction_details(self):
        self.config_manager.get_interaction_details.return_value = {}

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 500)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertIn(f"Couldn't determine workflow to invoke for interaction ID: {INTERACTION_NAME}",
                      response.body.decode())

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_not_called()

    def test_post_message_where_interaction_detail_has_invalid_workflow(self):
        self.config_manager.get_interaction_details.return_value = {'workflow': 'nonexistent workflow'}

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 500)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertIn(f"Couldn't determine workflow to invoke for interaction ID: {INTERACTION_NAME}",
                      response.body.decode())

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_not_called()

    def test_post_with_no_interaction_name(self):
        response = self.fetch("/", method="POST", body="A request")

        self.assertEqual(response.code, 404)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertIn('Required Interaction-Id header not found', response.body.decode())

    def test_post_with_invalid_interaction_name(self):
        self.config_manager.get_interaction_details.return_value = None

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                              body="A request")

        self.assertEqual(response.code, 404)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertIn(f'Unknown interaction ID: {INTERACTION_NAME}', response.body.decode())

    def test_post_with_no_body(self):
        self.config_manager.get_interaction_details.return_value = None

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                              body="")

        self.assertEqual(response.code, 400)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertIn("Body missing from request", response.body.decode())

    def test_handler_updates_store_for_sync_async(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result
        self.config_manager.get_interaction_details.return_value = {'sync-async': True, 'workflow': WORKFLOW_NAME}

        self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                   body=REQUEST_BODY)

        wdo.set_outbound_status.assert_called_with(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED)

    @patch('outbound.request.synchronous.handler.SynchronousHandler._write_response')
    def test_handler_updates_store_for_sync_async_failure_response(self, write_mock):
        write_mock.side_effect = Exception('Dam the connection was closed')
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result

        self.config_manager.get_interaction_details.return_value = {'sync-async': 'true', 'workflow': WORKFLOW_NAME}
        self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                   body=REQUEST_BODY)

        wdo.set_outbound_status.assert_called_with(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND)

    def test_sync_async_workflow_invoked(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result
        self.config_manager.get_interaction_details.return_value = {'sync-async': True, 'workflow': WORKFLOW_NAME}

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                              body=REQUEST_BODY)

        self.sync_async_workflow.handle_sync_async_outbound_message.assert_called_once()
        self.assertEqual(expected_response.encode(), response.body)

    def test_sync_async_workflow_not_invoked(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response))

        self.workflow.handle_outbound_message.return_value = result

        self.config_manager.get_interaction_details.return_value = {'sync-async': 'False', 'workflow': WORKFLOW_NAME}

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'false'},
                              body=REQUEST_BODY)

        self.sync_async_workflow.handle_sync_async_outbound_message.assert_not_called()
        self.workflow.handle_outbound_message.assert_called_once()
        self.assertEqual(expected_response.encode(), response.body)

    def test_error_when_no_sync_async_header_present(self):
        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 400)
        self.assertIn("Sync-Async header missing", response.body.decode())

    def test_error_when_sync_async_header_not_interactions(self):
        self.config_manager.get_interaction_details.return_value = {'workflow': WORKFLOW_NAME}

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 500)
        self.assertIn(" Failed to parse sync-async flag from interactions file for this interaction,"
                      " contact your administrator",
                      response.body.decode())

    def test_correct_workflow_called(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, "Success"))

        with self.subTest("Assert Sync-async called when interactions.json = false and header=false"):
            self.config_manager.get_interaction_details.return_value = {'sync-async': 'false',
                                                                        'workflow': WORKFLOW_NAME}
            self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'false'},
                       body=REQUEST_BODY)
            self.workflow.handle_outbound_message.assert_called_once()

    def test_sync_async_when_interactions_and_header_are_true(self):
        self.setup_workflows()

        self.config_manager.get_interaction_details.return_value = {'sync-async': True, 'workflow': WORKFLOW_NAME}
        self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                   body=REQUEST_BODY)
        self.sync_async_workflow.handle_sync_async_outbound_message.assert_called_once()

    def test_error_when_interactions_is_false_and_header_is_true(self):
        self.setup_workflows()
        self.config_manager.get_interaction_details.return_value = {'sync-async': False, 'workflow': WORKFLOW_NAME}
        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'true'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 400)
        self.assertIn("Message header requested sync-async wrap for a message patternthat does not support sync-async",
                      response.body.decode())
        self.sync_async_workflow.handle_sync_async_outbound_message.assert_not_called()
        self.workflow.handle_outbound_message.assert_not_called()

    def test_not_sync_async_when_interactions_is_true_and_header_is_false(self):
        self.setup_workflows()
        self.config_manager.get_interaction_details.return_value = {'sync-async': 'true', 'workflow': WORKFLOW_NAME}
        self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'false'},
                   body=REQUEST_BODY)
        self.sync_async_workflow.handle_sync_async_outbound_message.assert_not_called()
        self.workflow.handle_outbound_message.assert_called_once()

    def test_not_sync_async_when_interactions_is_false_header_is_false(self):
        self.setup_workflows()
        self.config_manager.get_interaction_details.return_value = {'sync-async': 'false', 'workflow': WORKFLOW_NAME}
        self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME, 'sync-async': 'false'},
                   body=REQUEST_BODY)
        self.sync_async_workflow.handle_sync_async_outbound_message.assert_not_called()
        self.workflow.handle_outbound_message.assert_called_once()

    def setup_workflows(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, "Success"))
