from unittest import TestCase
from unittest.mock import Mock, sentinel, patch

import utilities.message_utilities as message_utilities

import common.messages.ebxml_envelope as ebxml_envelope
import common.messages.ebxml_request_envelope as ebxml_request_envelope
import common.workflow.common as common_workflow
import common.workflow.sync_async as sync_async

PARTY_ID = "PARTY-ID"
MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"


class TestSyncAsyncWorkflow(TestCase):
    def setUp(self):
        self.mock_interactions_config = Mock()
        self.mock_transmission = Mock()

        self.workflow = sync_async.SyncAsyncWorkflow(self.mock_interactions_config, self.mock_transmission, PARTY_ID)

    @patch("common.messages.ebxml_request_envelope.EbxmlRequestEnvelope")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_prepare_message_async(self, mock_get_uuid, mock_envelope):
        mock_get_uuid.return_value = MOCK_UUID
        interaction_details = {sync_async.ASYNC_RESPONSE_EXPECTED: True}
        expected_context = {
            sync_async.ASYNC_RESPONSE_EXPECTED: True,
            ebxml_envelope.FROM_PARTY_ID: PARTY_ID,
            ebxml_envelope.CONVERSATION_ID: MOCK_UUID,
            ebxml_request_envelope.MESSAGE: sentinel.message
        }
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details
        mock_envelope.return_value.serialize.return_value = \
            sentinel.ebxml_id, sentinel.http_headers, sentinel.ebxml_message

        is_async, actual_id, actual_response = self.workflow.prepare_message(sentinel.interaction_name,
                                                                             sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        mock_envelope.assert_called_with(expected_context)
        self.assertTrue(mock_envelope.return_value.serialize.called)
        self.assertTrue(is_async)
        self.assertIs(sentinel.ebxml_id, actual_id)
        self.assertIs(sentinel.ebxml_message, actual_response)

    @patch("common.messages.ebxml_request_envelope.EbxmlRequestEnvelope")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_prepare_message_async_message_id_passed_in(self, mock_get_uuid, mock_envelope):
        mock_get_uuid.return_value = MOCK_UUID
        expected_context = {
            ebxml_envelope.MESSAGE_ID: sentinel.message_id,
            sync_async.ASYNC_RESPONSE_EXPECTED: True,
            ebxml_envelope.FROM_PARTY_ID: PARTY_ID,
            ebxml_envelope.CONVERSATION_ID: MOCK_UUID,
            ebxml_request_envelope.MESSAGE: sentinel.message
        }
        interaction_details = {sync_async.ASYNC_RESPONSE_EXPECTED: True}
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details
        mock_envelope.return_value.serialize.return_value = \
            sentinel.ebxml_id, sentinel.http_headers, sentinel.ebxml_message

        is_async, actual_id, actual_response = self.workflow.prepare_message(sentinel.interaction_name,
                                                                             sentinel.message,
                                                                             sentinel.message_id)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        mock_envelope.assert_called_with(expected_context)
        self.assertTrue(mock_envelope.return_value.serialize.called)
        self.assertTrue(is_async)
        self.assertIs(sentinel.ebxml_id, actual_id)
        self.assertIs(sentinel.ebxml_message, actual_response)

    def test_prepare_message_sync(self):
        interaction_details = {sync_async.ASYNC_RESPONSE_EXPECTED: False}
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details

        is_async, actual_id, actual_response = self.workflow.prepare_message(sentinel.interaction_name,
                                                                             sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.assertFalse(is_async)
        self.assertIsNone(actual_id)
        self.assertIs(sentinel.message, actual_response)

    def test_prepare_message_incorrect_interaction_name(self):
        self.mock_interactions_config.get_interaction_details.return_value = None

        with (self.assertRaises(common_workflow.UnknownInteractionError)):
            self.workflow.prepare_message("unknown_interaction", "message")

    def test_send_message(self):
        self.mock_interactions_config.get_interaction_details.return_value = sentinel.interaction_details
        self.mock_transmission.make_request.return_value = sentinel.response

        actual_response = self.workflow.send_message(sentinel.interaction_name, sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.mock_transmission.make_request.assert_called_with(sentinel.interaction_details, sentinel.message)
        self.assertIs(sentinel.response, actual_response)

    def test_send_message_incorrect_interaction_name(self):
        self.mock_interactions_config.get_interaction_details.return_value = None

        with (self.assertRaises(common_workflow.UnknownInteractionError)):
            self.workflow.send_message("unknown_interaction", "message")
