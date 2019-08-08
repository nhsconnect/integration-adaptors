import unittest.mock

import tornado.testing
import tornado.web

from workflow import common as common_workflow
import request.synchronous.handler as handler

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
INTERACTION_NAME = "interaction"
REQUEST_BODY = "A request"


class TestSynchronousHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        self.workflow = unittest.mock.Mock()
        return tornado.web.Application([
            (r"/(.*)", handler.SynchronousHandler, dict(workflow=self.workflow, callbacks={}, async_timeout=1))
        ])

    def test_post_synchronous_message(self):
        expected_response = "Hello world!"
        self.workflow.prepare_message.return_value = False, None, REQUEST_BODY
        self.workflow.send_message.return_value = expected_response

        response = self.fetch(f"/{INTERACTION_NAME}", method="POST", body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/xml")
        self.assertEqual(response.body.decode(), expected_response)
        self.workflow.send_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY)

    def test_post_message_with_message_id_passed_in(self):
        message_id = "message-id"
        expected_response = "Hello world!"
        self.workflow.prepare_message.return_value = False, None, REQUEST_BODY
        self.workflow.send_message.return_value = expected_response

        response = self.fetch(f"/{INTERACTION_NAME}?messageId={message_id}", method="POST", body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        self.workflow.prepare_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY, message_id)
        self.workflow.send_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY)

    def test_post_with_invalid_interaction_name(self):
        self.workflow.prepare_message.side_effect = common_workflow.UnknownInteractionError(INTERACTION_NAME)

        response = self.fetch(f"/{INTERACTION_NAME}", method="POST", body="A request")

        self.assertEqual(response.code, 404)

    def test_post_asynchronous_message_times_out(self):
        # An request that results in an asynchronous message should time out if no asynchronous response is received.
        self.workflow.prepare_message.return_value = True, MOCK_UUID, "ebXML request"
        self.workflow.send_message.return_value = "Hello world!"

        response = self.fetch(f"/{INTERACTION_NAME}", method="POST", body="A request")

        self.assertEqual(response.code, 500)
