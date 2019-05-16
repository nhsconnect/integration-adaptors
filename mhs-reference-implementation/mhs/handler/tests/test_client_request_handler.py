from unittest.mock import Mock

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from mhs.handler.client_request_handler import ClientRequestHandler
from mhs.sender.sender import UnknownInteractionError

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
INTERACTION_NAME = "interaction"
REQUEST_BODY = "A request"


class TestClientRequestHandler(AsyncHTTPTestCase):

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r"/.*", ClientRequestHandler, dict(sender=self.sender, callbacks={}, async_timeout=1))
        ])

    def test_post_synchronous_message(self):
        expected_response = "Hello world!"
        self.sender.prepare_message.return_value = False, None, REQUEST_BODY
        self.sender.send_message.return_value = expected_response

        response = self.fetch(f"/{INTERACTION_NAME}", method="POST", body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/xml")
        self.assertEqual(response.body.decode(), expected_response)
        self.sender.send_message.assert_called_with(INTERACTION_NAME, REQUEST_BODY)

    def test_post_with_invalid_interaction_name(self):
        self.sender.prepare_message.side_effect = UnknownInteractionError(INTERACTION_NAME)

        response = self.fetch(f"/{INTERACTION_NAME}", method="POST", body="A request")

        self.assertEqual(response.code, 404)

    def test_post_asynchronous_message_times_out(self):
        # An request that results in an asynchronous message should time out if no asynchronous response is received.
        self.sender.prepare_message.return_value = True, MOCK_UUID, "ebXML request"
        self.sender.send_message.return_value = "Hello world!"

        response = self.fetch(f"/{INTERACTION_NAME}", method="POST", body="A request")

        self.assertEqual(response.code, 500)
