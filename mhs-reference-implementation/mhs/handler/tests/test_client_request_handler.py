from unittest.mock import Mock

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from mhs.handler.client_request_handler import ClientRequestHandler
from mhs.sender.sender import UnknownInteractionError

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"


class TestAsyncResponseHandler(AsyncHTTPTestCase):

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r"/.*", ClientRequestHandler, dict(sender=self.sender))
        ])

    def test_post(self):
        interaction_name = "interaction"
        request_body = "A request"
        expected_response = "Hello world!"
        self.sender.send_message.return_value = MOCK_UUID, expected_response

        response = self.fetch(f"/{interaction_name}", method="POST", body=request_body)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/xml")
        self.assertEqual(response.body.decode(), expected_response)
        self.sender.send_message.assert_called_with(interaction_name, request_body)

    def test_post_with_invalid_interaction_name(self):
        interaction_name = "invalid"
        request_body = "A request"
        self.sender.send_message.side_effect = UnknownInteractionError(interaction_name)

        response = self.fetch(f"/{interaction_name}", method="POST", body=request_body)

        self.assertEqual(response.code, 404)
