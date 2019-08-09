import unittest.mock
from unittest.mock import patch

import tornado.testing
import tornado.web

import mhs.common.workflow.common as common_workflow
import mhs.outbound.request.synchronous.handler as handler
from utilities import message_utilities
from utilities import integration_adaptors_logger as log
MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
MOCK_UUID_2 = "82B5FE90-FD7C-41AC-82A3-9032FB0317FB"
INTERACTION_NAME = "interaction"
REQUEST_BODY = "A request"


class TestSynchronousHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        self.workflow = unittest.mock.Mock()
        return tornado.web.Application([
            (r"/", handler.SynchronousHandler, dict(workflow=self.workflow, callbacks={}, async_timeout=1))
        ])

    def tearDown(self):
        log.message_id.set(None)
        log.correlation_id.set(None)

    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    @patch.object(log, "correlation_id")
    @patch.object(log, "message_id")
    def test_post_synchronous_message(self, mock_message_id, mock_correlation_id, mock_get_uuid):
        expected_response = "Hello world!"
        self.workflow.prepare_message.return_value = False, REQUEST_BODY
        self.workflow.send_message.return_value = expected_response
        mock_get_uuid.side_effect = [MOCK_UUID, MOCK_UUID_2]

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME}, body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/xml")
        self.assertEqual(response.body.decode(), expected_response)

        self.workflow.prepare_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY, MOCK_UUID)
        self.workflow.send_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY)

        mock_message_id.set.assert_called_with(MOCK_UUID)
        mock_correlation_id.set.assert_called_with(MOCK_UUID_2)

    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    @patch.object(log, "correlation_id")
    @patch.object(log, "message_id")
    def test_post_message_with_message_id_passed_in(self, mock_message_id, mock_correlation_id, mock_get_uuid):
        message_id = "message-id"
        expected_response = "Hello world!"
        self.workflow.prepare_message.return_value = False, REQUEST_BODY
        self.workflow.send_message.return_value = expected_response
        mock_get_uuid.return_value = MOCK_UUID

        response = self.fetch("/", method="POST",
                              headers={"Interaction-Id": INTERACTION_NAME, "Message-Id": message_id}, body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        mock_get_uuid.assert_called_once()

        self.workflow.prepare_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY, message_id)
        self.workflow.send_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY)

        mock_message_id.set.assert_called_with(message_id)
        mock_correlation_id.set.assert_called_with(MOCK_UUID)

    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    @patch.object(log, "correlation_id")
    @patch.object(log, "message_id")
    def test_post_message_with_correlation_id_passed_in(self, mock_message_id, mock_correlation_id, mock_get_uuid):
        correlation_id = "correlation-id"
        expected_response = "Hello world!"
        self.workflow.prepare_message.return_value = False, REQUEST_BODY
        self.workflow.send_message.return_value = expected_response
        mock_get_uuid.return_value = MOCK_UUID

        response = self.fetch("/", method="POST",
                              headers={"Interaction-Id": INTERACTION_NAME, "Correlation-Id": correlation_id},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        mock_get_uuid.assert_called_once()

        self.workflow.prepare_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY, MOCK_UUID)
        self.workflow.send_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY)

        mock_message_id.set.assert_called_with(MOCK_UUID)
        mock_correlation_id.set.assert_called_with(correlation_id)

    def test_post_with_no_interaction_name(self):
        response = self.fetch("/", method="POST", body="A request")

        self.assertEqual(response.code, 404)

    def test_post_with_invalid_interaction_name(self):
        self.workflow.prepare_message.side_effect = common_workflow.UnknownInteractionError(INTERACTION_NAME)

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME}, body="A request")

        self.assertEqual(response.code, 404)

    def test_post_asynchronous_message_times_out(self):
        # A request that results in an asynchronous message should time out if no asynchronous response is received.
        self.workflow.prepare_message.return_value = True, MOCK_UUID, "ebXML request"
        self.workflow.send_message.return_value = "Hello world!"

        response = self.fetch("/", method="POST", headers={"Interaction-Id": INTERACTION_NAME}, body="A request")

        self.assertEqual(response.code, 500)
