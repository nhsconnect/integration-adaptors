import json
import unittest.mock
import urllib.error
import urllib.request
from unittest.mock import patch

import tornado.httpclient
import tornado.testing
import tornado.util
import tornado.web

from utilities import mdc
from mhs_common.workflow import synchronous
from utilities import test_utilities
from utilities import message_utilities

from outbound.request.synchronous import handler

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
MOCK_UUID_2 = "82B5FE90-FD7C-41AC-82A3-9032FB0317FB"
INTERACTION_NAME = "interaction"
REQUEST_BODY_PAYLOAD = "A request"
REQUEST_BODY = json.dumps({"payload": REQUEST_BODY_PAYLOAD})
WORKFLOW_NAME = "workflow name"
INTERACTION_DETAILS = {'workflow': WORKFLOW_NAME, 'sync_async': True}
SYNC_ASYNC_WORKFLOW = "sync-async"
CORRELATION_ID = '12345'


class BaseHandlerTest(tornado.testing.AsyncHTTPTestCase):

    def tearDown(self):
        mdc.message_id.set(None)
        mdc.correlation_id.set(None)

    def call_handler(self, content_type="application/json", interaction_id=INTERACTION_NAME, body=REQUEST_BODY,
                     wait_for_response='false', correlation_id=CORRELATION_ID) -> tornado.httpclient.HTTPResponse:
        return self.fetch("/", method="POST",
                          headers={"Content-Type": content_type, "Interaction-Id": interaction_id,
                                   'wait-for-response': wait_for_response, "Correlation-Id": correlation_id},
                          body=body)


class TestSynchronousHandler(BaseHandlerTest):

    def get_app(self):
        self.workflow = unittest.mock.Mock()
        self.workflow.workflow_specific_interaction_details = dict()
        self.sync_async_workflow = unittest.mock.MagicMock()
        self.config_manager = unittest.mock.Mock()
        return tornado.web.Application([
            (r"/", handler.SynchronousHandler,
             dict(config_manager=self.config_manager, workflows={WORKFLOW_NAME: self.workflow,
                                                                 SYNC_ASYNC_WORKFLOW: self.sync_async_workflow}))
        ])

    @patch.object(message_utilities, "get_uuid")
    @patch.object(mdc, "correlation_id")
    @patch.object(mdc, "message_id")
    def test_post_message(self, mock_message_id, mock_correlation_id, mock_get_uuid):
        expected_response = "Hello world!"
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, expected_response, None))
        mock_get_uuid.side_effect = [MOCK_UUID, MOCK_UUID_2]
        self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

        response = self.call_handler(correlation_id=MOCK_UUID_2)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/xml")
        self.assertEqual(response.headers["Message-Id"], MOCK_UUID)
        self.assertEqual(response.headers["Correlation-Id"], MOCK_UUID_2)
        self.assertEqual(response.body.decode(), expected_response)

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_called_with(None, MOCK_UUID, MOCK_UUID_2, INTERACTION_DETAILS,
                                                                 REQUEST_BODY_PAYLOAD, None)

        mock_message_id.set.assert_called_with(MOCK_UUID)
        mock_correlation_id.set.assert_called_with(MOCK_UUID_2)

    def test_post_message_works_correctly_when_attachment_is_a_valid_content_type(self):
        textual_content_types = ['text/plain', 'text/html', 'text/xml', 'application/xml', 'text/rtf']
        binary_content_types = ['application/pdf', 'audio/basic', 'audio/mpeg', 'image/png', 'image/gif', 'image/jpeg',
                                'image/tiff', 'video/mpeg', 'application/msword', 'application/octet-stream']
        textual_sub_tests = [(False, content_type, 'test') for content_type in textual_content_types]
        binary_sub_tests = [(True, content_type, 'iVBORw0KGgoAAA==') for content_type in binary_content_types]
        for is_base64, content_type, payload in textual_sub_tests + binary_sub_tests:
            with self.subTest(content_type=content_type):
                self.workflow.handle_outbound_message.return_value = test_utilities.awaitable(
                    (200, "Hello world!", None))
                self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

                body = {
                    "payload": REQUEST_BODY_PAYLOAD,
                    "attachments": [{
                        "is_base64": is_base64,
                        "content_type": content_type,
                        "payload": payload,
                        "description": "some description"
                    }]}
                response = self.call_handler(body=json.dumps(body))

                self.assertEqual(response.code, 200)
                self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)

    @patch.object(message_utilities, "get_uuid")
    @patch.object(mdc, "correlation_id")
    @patch.object(mdc, "message_id")
    def test_post_message_with_message_id_passed_in(self, mock_message_id, mock_correlation_id, mock_get_uuid):
        message_id = "message-id"
        expected_response = "Hello world!"
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, expected_response, None))
        mock_get_uuid.return_value = MOCK_UUID
        self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

        response = self.fetch("/", method="POST",
                              headers={"Content-Type": "application/json", "Interaction-Id": INTERACTION_NAME,
                                       "Message-Id": message_id,
                                       'wait-for-response': 'false'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        self.assertEqual(response.headers["Correlation-Id"], MOCK_UUID)
        mock_get_uuid.assert_called()

        self.workflow.handle_outbound_message.assert_called_with(None, message_id, MOCK_UUID, INTERACTION_DETAILS,
                                                                 REQUEST_BODY_PAYLOAD, None)

        mock_message_id.set.assert_called_with(message_id)
        mock_correlation_id.set.assert_called_with(MOCK_UUID)

    @patch.object(message_utilities, "get_uuid")
    def test_post_message_with_correlation_id_passed_in_should_call_workflow(self, mock_get_uuid):
        expected_response = "Hello world!"
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, expected_response, None))
        mock_get_uuid.return_value = MOCK_UUID
        self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

        response = self.fetch("/", method="POST",
                              headers={"Content-Type": "application/json", "Interaction-Id": INTERACTION_NAME,
                                       "Correlation-Id": CORRELATION_ID,
                                       'wait-for-response': 'false'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), expected_response)
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertEqual(response.headers["Message-Id"], MOCK_UUID)
        mock_get_uuid.assert_called_once()

        self.workflow.handle_outbound_message.assert_called_with(None, MOCK_UUID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                 REQUEST_BODY_PAYLOAD, None)

    @patch.object(message_utilities, "get_uuid")
    @patch.object(mdc, "correlation_id")
    @patch.object(mdc, "message_id")
    @patch.object(mdc, 'interaction_id')
    def test_handler_should_set_logging_context_variables_on_successful_request(self,
                                                                                mock_interaction_id,
                                                                                mock_message_id,
                                                                                mock_correlation_id,
                                                                                mock_get_uuid):
        correlation_id = "correlation-id"
        expected_response = "Hello world!"
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable(
            (200, expected_response, None))
        mock_get_uuid.return_value = MOCK_UUID
        self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

        self.fetch("/", method="POST",
                   headers={"Content-Type": "application/json", "Interaction-Id": INTERACTION_NAME,
                            "Correlation-Id": correlation_id,
                            'wait-for-response': 'false'},
                   body=REQUEST_BODY)

        mock_message_id.set.assert_called_with(MOCK_UUID)
        mock_correlation_id.set.assert_called_with(correlation_id)
        mock_interaction_id.set.assert_called_with(INTERACTION_NAME)

    def test_post_message_where_workflow_returns_error_response(self):
        for http_status in [400, 409, 500, 503]:
            with self.subTest(http_status=http_status):
                expected_response = "Error response body"
                self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((http_status,
                                                                                               expected_response, None))
                self.config_manager.get_interaction_details.return_value = INTERACTION_DETAILS

                response = self.call_handler()

                self.assertEqual(response.code, http_status)
                self.assertEqual(response.headers["Content-Type"], "text/plain")
                self.assertIn("Correlation-Id", response.headers, 'Correllation-Id header should be present in error response')
                self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
                self.assertEqual(response.body.decode(), expected_response)

    def test_post_message_where_workflow_not_found_on_interaction_details(self):
        self.config_manager.get_interaction_details.return_value = {}

        response = self.call_handler()

        self.assertEqual(response.code, 500)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn("Correlation-Id", response.headers, 'Correllation-Id header should be present in error response')
        self.assertIn(f"Couldn't determine workflow to invoke for interaction ID: {INTERACTION_NAME}",
                      response.body.decode())

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_not_called()

    def test_post_message_returns_correct_status_line_in_error_response(self):
        """
        At one point the error response being returned had the response body being additionally set as the textual
        phrase on the status line (see https://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html#sec6.1). This test
        checks that this isn't being done.
        """
        response = self.fetch("/", method="POST", body="A request", headers={"Correlation-Id": CORRELATION_ID})

        self.assertEqual(response.code, 404)
        self.assertEqual(response.error.message, "Not Found")
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(CORRELATION_ID, response.headers["Correlation-Id"])
        self.assertIn('Required Interaction-Id header not found', response.body.decode())

    def test_post_message_where_interaction_detail_has_invalid_workflow(self):
        self.config_manager.get_interaction_details.return_value = {'workflow': 'nonexistent workflow'}

        response = self.call_handler()

        self.assertEqual(response.code, 500)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn(f"Couldn't determine workflow to invoke for interaction ID: {INTERACTION_NAME}",
                      response.body.decode())

        self.config_manager.get_interaction_details.assert_called_with(INTERACTION_NAME)
        self.workflow.handle_outbound_message.assert_not_called()

    def test_post_with_no_interaction_name(self):
        response = self.fetch("/", method="POST", body="A request", headers={"Correlation-Id": CORRELATION_ID})

        self.assertEqual(response.code, 404)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn('Required Interaction-Id header not found', response.body.decode())

    @patch.object(message_utilities, "get_uuid")
    def test_post_with_no_correlation_id_assigns_new_correlation_id(self, mock_get_uuid):

        mock_get_uuid.return_value = MOCK_UUID
        response = self.fetch("/", method="POST",
                              headers={"Content-Type": "application/json", "Interaction-Id": INTERACTION_NAME,
                                       'wait-for-response': 'false'},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 500)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], MOCK_UUID)
        self.assertIn("Correlation-Id", response.headers)


    def test_post_with_invalid_interaction_name(self):
        self.config_manager.get_interaction_details.return_value = None

        response = self.call_handler()

        self.assertEqual(response.code, 404)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn(f'Unknown interaction ID: {INTERACTION_NAME}', response.body.decode())

    @tornado.testing.gen_test
    async def test_post_with_no_content_type_header(self):
        # Tornado's default simple_httpclient will set the Content-Type header to application/x-www-form-urlencoded
        # by default if it is not set to anything. So we use urllib here instead to avoid this behaviour and make a
        # HTTP request with no Content-Type.
        request = urllib.request.Request(url=self.get_url("/"), method="POST",
                                         headers={"Interaction-Id": INTERACTION_NAME, 'wait-for-response': 'true'})

        def perform_request():
            urllib.request.urlopen(request)

        with self.assertRaisesRegex(urllib.error.HTTPError, 'Bad Request'):
            await self.io_loop.run_in_executor(executor=None, func=perform_request)

    def test_post_with_no_body(self):
        self.config_manager.get_interaction_details.return_value = None

        response = self.call_handler(body="")

        self.assertEqual(response.code, 400)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn("Body missing from request", response.body.decode())

    def test_post_with_non_json_body(self):
        self.config_manager.get_interaction_details.return_value = None

        response = self.call_handler(content_type="text/plain", body="non-JSON body")

        self.assertEqual(response.code, 415)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn("Unsupported content type", response.body.decode())

    def test_post_with_invalid_json_body(self):
        self.config_manager.get_interaction_details.return_value = None

        response = self.call_handler(body="{]")

        self.assertEqual(response.code, 400)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn("Invalid JSON request body", response.body.decode())

    def test_handler_updates_store_for_wait_for_response(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result
        self.sync_async_workflow.set_successful_message_response.return_value = test_utilities.awaitable(None)
        self.config_manager.get_interaction_details.return_value = {'sync_async': True, 'workflow': WORKFLOW_NAME}

        self.call_handler(wait_for_response='true')

        self.sync_async_workflow.set_successful_message_response.assert_called_once_with(wdo)

    @patch('outbound.request.synchronous.handler.SynchronousHandler._write_response')
    def test_handler_updates_store_for_wait_for_response_failure_response(self, write_mock):
        write_mock.side_effect = Exception('Dam the connection was closed')
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result
        self.sync_async_workflow.set_failure_message_response.return_value = test_utilities.awaitable(None)

        self.config_manager.get_interaction_details.return_value = {'sync_async': True, 'workflow': WORKFLOW_NAME}

        self.call_handler(wait_for_response='true')

        self.sync_async_workflow.set_failure_message_response.assert_called_once_with(wdo)

    def test_sync_async_workflow_invoked(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result
        self.sync_async_workflow.set_successful_message_response.return_value = test_utilities.awaitable(None)

        self.config_manager.get_interaction_details.return_value = {'sync_async': True, 'workflow': WORKFLOW_NAME}

        response = self.call_handler(wait_for_response='true')

        self.sync_async_workflow.handle_sync_async_outbound_message.assert_called_once()
        self.assertEqual(expected_response.encode(), response.body)
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)

    def test_sync_async_workflow_not_invoked(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, None))

        self.workflow.handle_outbound_message.return_value = result
        self.workflow.set_successful_message_response.return_value = test_utilities.awaitable(None)

        self.config_manager.get_interaction_details.return_value = {'sync_async': False, 'workflow': WORKFLOW_NAME}

        response = self.call_handler(wait_for_response='false')

        self.sync_async_workflow.handle_sync_async_outbound_message.assert_not_called()
        self.workflow.handle_outbound_message.assert_called_once()
        self.assertEqual(expected_response.encode(), response.body)
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)

    def test_error_when_no_wait_for_response_header_present(self):
        response = self.fetch("/", method="POST",
                              headers={"Interaction-Id": INTERACTION_NAME, "Correlation-Id": CORRELATION_ID},
                              body=REQUEST_BODY)

        self.assertEqual(response.code, 400)
        self.assertEqual(CORRELATION_ID, response.headers["Correlation-Id"])
        self.assertIn("wait-for-response header missing", response.body.decode())

    def test_error_when_sync_async_not_interactions(self):
        self.config_manager.get_interaction_details.return_value = {'workflow': WORKFLOW_NAME}

        response = self.call_handler(wait_for_response='true')

        self.assertEqual(response.code, 500)
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn("Failed to find sync-async flag for the interaction within the interactions.json",
                      response.body.decode())

    def test_correct_workflow_called(self):
        self.setup_workflows()
        self.config_manager.get_interaction_details.return_value = {'sync_async': False,
                                                                    'workflow': WORKFLOW_NAME}

        self.call_handler()

        self.workflow.handle_outbound_message.assert_called_once()

    def test_sync_async_when_interactions_and_wait_for_response_header_are_true(self):
        self.setup_workflows()

        self.config_manager.get_interaction_details.return_value = {'sync_async': True, 'workflow': WORKFLOW_NAME}

        self.call_handler(wait_for_response='true')

        self.sync_async_workflow.handle_sync_async_outbound_message.assert_called_once()

    def test_error_when_interactions_is_false_and_wait_for_response_header_is_true(self):
        self.setup_workflows()
        self.config_manager.get_interaction_details.return_value = {'sync_async': False, 'workflow': WORKFLOW_NAME}

        response = self.call_handler(wait_for_response='true')

        self.assertEqual(response.code, 400)
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        self.assertIn("Message header requested wait-for-response wrap for a message pattern that does not support sync-async",
                      response.body.decode())
        self.sync_async_workflow.handle_sync_async_outbound_message.assert_not_called()
        self.workflow.handle_outbound_message.assert_not_called()

    def test_not_sync_async_when_interactions_is_true_and_wait_for_response_header_is_false(self):
        self.setup_workflows()
        self.config_manager.get_interaction_details.return_value = {'sync_async': True, 'workflow': WORKFLOW_NAME}

        self.call_handler(wait_for_response='false')

        self.sync_async_workflow.handle_sync_async_outbound_message.assert_not_called()
        self.workflow.handle_outbound_message.assert_called_once()

    def test_not_sync_async_when_interactions_is_false_and_wait_for_response_header_is_false(self):
        self.setup_workflows()
        self.config_manager.get_interaction_details.return_value = {'sync_async': False, 'workflow': WORKFLOW_NAME}

        self.call_handler(wait_for_response='false')

        self.sync_async_workflow.handle_sync_async_outbound_message.assert_not_called()
        self.workflow.handle_outbound_message.assert_called_once()

    def setup_workflows(self):
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.sync_async_workflow.handle_sync_async_outbound_message.return_value = result
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, "Success"))


class TestSynchronousHandlerRequestBodyValidation(BaseHandlerTest):

    def get_app(self):
        return tornado.web.Application([
            (r"/", handler.SynchronousHandler,
             dict(config_manager="unused in these tests", workflows={}))
        ])

    def test_post_with_missing_field_in_request_body(self):
        sub_tests = [
            {"request_body": {}, "field_name": "payload"},
            {"request_body": {"payload": "test", "attachments": [
                {"content_type": "text/plain", "payload": "blah", "description": "some description"}]},
             "field_name": "is_base64"},
            {"request_body": {"payload": "test", "attachments": [
                {"is_base64": False, "payload": "blah", "description": "some description"}]},
             "field_name": "content_type"},
            {"request_body": {"payload": "test", "attachments": [
                {"is_base64": False, "content_type": "text/plain", "description": "some description"}]},
             "field_name": "payload"},
            {"request_body": {"payload": "test",
                              "attachments": [{"is_base64": False, "content_type": "text/plain", "payload": "blah"}]},
             "field_name": "description"},
        ]
        for sub_test in sub_tests:
            with self.subTest(missing_field=sub_test["field_name"]):
                response_body = self._make_request_and_check_invalid_request_response(sub_test)
                self.assertIn("Missing data for required field", response_body)

    def test_post_with_field_of_incorrect_type_in_request_body(self):
        sub_tests = [
            {"request_body": {"payload": True}, "field_name": "payload"},
            {"request_body": {"payload": "test", "attachments": ""}, "field_name": "attachments"},
            {"request_body": {"payload": "test", "attachments": [
                {"is_base64": False, "content_type": False, "payload": "blah", "description": "some description"}]},
             "field_name": "content_type"},
            {"request_body": {"payload": "test", "attachments": [
                {"is_base64": False, "content_type": "text/plain", "payload": [], "description": "some description"}]},
             "field_name": "payload"},
            {"request_body": {"payload": "test", "attachments": [
                {"is_base64": False, "content_type": "text/plain", "payload": "blah", "description": 45}]},
             "field_name": "description"},
        ]
        for sub_test in sub_tests:
            with self.subTest(field_with_empty_string=sub_test["field_name"]):
                response_body = self._make_request_and_check_invalid_request_response(sub_test)
                self.assertTrue("Not a valid" in response_body or "Invalid type" in response_body,
                                msg=f"Incorrect error response body when {sub_test['field_name']} is incorrect type: "
                                f"{response_body}")

    def test_post_with_is_base64_field_not_bool_but_bool_like_string_in_request_body(self):
        for bool_like_string in ["True", "t", "False", "f"]:
            with self.subTest(bool_like_string=bool_like_string):
                request_body = {"payload": "test",
                                "attachments": [{
                                    "is_base64": bool_like_string,
                                    "content_type": "text/plain",
                                    "payload": "blah",
                                    "description": "some description"}]}
                response_body = self._make_request_and_check_invalid_request_response(
                    {'request_body': request_body, 'field_name': "is_base64"})
                self.assertIn("Not a valid boolean", response_body)

    def test_post_with_request_body_with_not_allowed_content_type(self):
        request_body = {"payload": "test",
                        "attachments": [{
                            "is_base64": False,
                            "content_type": "application/zip",
                            "payload": "blah",
                            "description": "some description"}]}
        response_body = self._make_request_and_check_invalid_request_response(
            {'request_body': request_body, 'field_name': "content_type"})
        self.assertIn("Must be one of", response_body)

    def test_post_with_request_body_with_attachment_payload_wrong_size(self):
        payloads = ["", "e" * 5_000_001]
        for payload in payloads:
            with self.subTest(payload_size=len(payload)):
                request_body = {"payload": "test",
                                "attachments": [{
                                    "is_base64": False,
                                    "content_type": "text/plain",
                                    "payload": payload,
                                    "description": "some description"}]}
                response_body = self._make_request_and_check_invalid_request_response(
                    {'request_body': request_body, 'field_name': "payload"})
                self.assertIn("Length must be between 1 and 5000000", response_body)

    def test_post_with_request_body_with_hl7_payload_wrong_size(self):
        payloads = ["", "e" * 5_000_001]
        for payload in payloads:
            with self.subTest(payload_size=len(payload)):
                request_body = {"payload": payload}
                response_body = self._make_request_and_check_invalid_request_response(
                    {'request_body': request_body, 'field_name': "payload"})
                self.assertIn("Length must be between 1 and 5000000", response_body)

    def test_post_with_request_body_with_attachment_description_wrong_size(self):
        descriptions = ["", "e" * 101]
        for description in descriptions:
            with self.subTest(description_size=len(description)):
                request_body = {"payload": "test",
                                "attachments": [{
                                    "is_base64": False,
                                    "content_type": "text/plain",
                                    "payload": "some payload",
                                    "description": description}]}
                response_body = self._make_request_and_check_invalid_request_response(
                    {'request_body': request_body, 'field_name': "description"})
                self.assertIn("Length must be between 1 and 100", response_body)

    def test_post_with_request_body_with_too_many_attachments(self):
        attachment = {
            "is_base64": False,
            "content_type": "text/plain",
            "payload": "blah",
            "description": "some description"}
        request_body = {"payload": "test",
                        "attachments": [attachment] * 99}
        response_body = self._make_request_and_check_invalid_request_response(
            {'request_body': request_body, 'field_name': "attachments"})
        self.assertIn("Longer than maximum length 98", response_body)

    def _make_request_and_check_invalid_request_response(self, sub_test: dict) -> str:
        response = self.call_handler(body=json.dumps(sub_test["request_body"]))

        self.assertEqual(response.code, 400)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
        response_body = response.body.decode()
        self.assertIn("Invalid request", response_body)
        self.assertIn(sub_test["field_name"], response_body)
        return response_body


class TestSynchronousHandlerSyncMessage(BaseHandlerTest):

    def get_app(self):
        self.workflow = unittest.mock.Mock(spec=synchronous.SynchronousWorkflow)
        self.workflow.workflow_specific_interaction_details = {}
        self.sync_async_workflow = unittest.mock.MagicMock()
        self.config_manager = unittest.mock.Mock()
        return tornado.web.Application([
            (r"/", handler.SynchronousHandler,
             dict(config_manager=self.config_manager, workflows={WORKFLOW_NAME: self.workflow,
                                                                 SYNC_ASYNC_WORKFLOW: self.sync_async_workflow}))
        ])

    def test_invoke_default_workflows_updates_state_for_sync(self):
        self.config_manager.get_interaction_details.return_value = {'sync_async': False, 'workflow': WORKFLOW_NAME}

        wdo_mock = unittest.mock.MagicMock()
        wdo_mock.set_outbound_status.return_value = test_utilities.awaitable(True)
        self.workflow.handle_outbound_message.return_value = test_utilities.awaitable((200, "Success", wdo_mock))
        self.workflow.set_successful_message_response.return_value = test_utilities.awaitable(None)

        self.call_handler()

        self.workflow.set_successful_message_response.assert_called_once_with(wdo_mock)

    @patch('outbound.request.synchronous.handler.SynchronousHandler._write_response')
    @patch('mhs_common.workflow.synchronous.SynchronousWorkflow')
    def test_handler_updates_store_for_sync_failure_response(self, sync_mock, write_mock):
        sync_mock.set_failure_message_response.return_value = test_utilities.awaitable(True)
        # self.workflow.set_failure_message_response.return_value = 5
        # self.workflow.set_success_message_response.return_value = 5
        write_mock.side_effect = Exception('Dam the connection was closed')
        expected_response = "Hello world!"
        wdo = unittest.mock.MagicMock()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        result = test_utilities.awaitable((200, expected_response, wdo))

        self.workflow.handle_outbound_message.return_value = result
        self.workflow.set_failure_message_response.return_value = test_utilities.awaitable(None)

        self.config_manager.get_interaction_details.return_value = {'sync_async': False, 'workflow': WORKFLOW_NAME}

        self.call_handler()

        self.workflow.set_failure_message_response.assert_called_once_with(wdo)

    def test_null_wdo_doesnt_error(self):
        expected_response = "Hello world!"
        result = test_utilities.awaitable((200, expected_response, None))

        self.workflow.handle_outbound_message.return_value = result
        self.config_manager.get_interaction_details.return_value = {'sync_async': False, 'workflow': WORKFLOW_NAME}

        response = self.call_handler()

        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Correlation-Id"], CORRELATION_ID)
