from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, sentinel, patch

from definitions import ROOT_DIR
from mhs.builder.ebxml_message_builder import CONVERSATION_ID, FROM_PARTY_ID
from mhs.builder.ebxml_request_message_builder import MESSAGE
from mhs.sender.sender import Sender, ASYNC_RESPONSE_EXPECTED, UnknownInteractionError
from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities

PARTY_ID = "PARTY_ID"


class TestSender(TestCase):
    def setUp(self):
        self.mock_interactions_config = Mock()
        self.mock_message_builder = Mock()
        self.mock_transport = Mock()

        self.sender = Sender(self.mock_interactions_config, self.mock_message_builder, self.mock_transport, PARTY_ID)

    @patch.object(MessageUtilities, "get_uuid")
    def test_prepare_message_async(self, mock_get_uuid):
        fixed_uuid = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_uuid.return_value = fixed_uuid
        interaction_details = {ASYNC_RESPONSE_EXPECTED: True}
        expected_context = {
            ASYNC_RESPONSE_EXPECTED: True,
            FROM_PARTY_ID: PARTY_ID,
            CONVERSATION_ID: fixed_uuid,
            MESSAGE: sentinel.message
        }
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details
        self.mock_message_builder.build_message.return_value = sentinel.ebxml_id, sentinel.ebxml_message

        is_async, actual_id, actual_response = self.sender.prepare_message(sentinel.interaction_name, sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.mock_message_builder.build_message.assert_called_with(expected_context)
        self.assertTrue(is_async)
        self.assertIs(sentinel.ebxml_id, actual_id)
        self.assertIs(sentinel.ebxml_message, actual_response)

    def test_prepare_message_sync(self):
        interaction_details = {ASYNC_RESPONSE_EXPECTED: False}
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details

        is_async, actual_id, actual_response = self.sender.prepare_message(sentinel.interaction_name, sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.assertFalse(is_async)
        self.assertIsNone(actual_id)
        self.assertIs(sentinel.message, actual_response)

    def test_build_message_incorrect_interaction_name(self):
        self.mock_interactions_config.get_interaction_details.return_value = None

        with (self.assertRaises(UnknownInteractionError)):
            self.sender.prepare_message("unknown_interaction", "message")

    def test_sender(self):
        self.mock_interactions_config.get_interaction_details.return_value = sentinel.interaction_details
        self.mock_transport.make_request.return_value = sentinel.response

        actual_response = self.sender.send_message(sentinel.interaction_name, sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.mock_transport.make_request.assert_called_with(sentinel.interaction_details, sentinel.message)
        self.assertIs(sentinel.response, actual_response)

    def test_send_message_incorrect_interaction_name(self):
        self.mock_interactions_config.get_interaction_details.return_value = None

        with (self.assertRaises(UnknownInteractionError)):
            self.sender.send_message("unknown_interaction", "message")
