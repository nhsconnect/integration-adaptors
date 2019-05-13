from unittest import TestCase
from unittest.mock import Mock, sentinel, patch

from mhs.builder.ebxml_message_builder import CONVERSATION_ID, FROM_PARTY_ID
from mhs.builder.ebxml_request_message_builder import MESSAGE
from mhs.sender.sender import Sender, WRAPPER_REQUIRED, UnknownInteractionError
from utilities.message_utilities import MessageUtilities

EXPECTED_PARTY_ID = "A91424-9199121"


class TestSender(TestCase):
    def setUp(self):
        self.mock_interactions_config = Mock()
        self.mock_message_builder = Mock()
        self.mock_transport = Mock()

        self.sender = Sender(self.mock_interactions_config, self.mock_message_builder, self.mock_transport)

    @patch.object(MessageUtilities, "get_uuid")
    def test_send_message_with_ebxml_wrapper(self, mock_get_uuid):
        fixed_uuid = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_uuid.return_value = fixed_uuid
        interaction_details = {WRAPPER_REQUIRED: True}
        expected_context = {
            WRAPPER_REQUIRED: True,
            FROM_PARTY_ID: EXPECTED_PARTY_ID,
            CONVERSATION_ID: fixed_uuid,
            MESSAGE: sentinel.message
        }
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details
        self.mock_message_builder.build_message.return_value = sentinel.ebxml_id, sentinel.ebxml_message
        self.mock_transport.make_request.return_value = sentinel.response

        actual_id, actual_response = self.sender.send_message(sentinel.interaction_name, sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.mock_message_builder.build_message.assert_called_with(expected_context)
        self.mock_transport.make_request.assert_called_with(interaction_details, sentinel.ebxml_message)
        self.assertIs(sentinel.ebxml_id, actual_id)
        self.assertIs(sentinel.response, actual_response)

    def test_send_message_without_ebxml_wrapper(self):
        interaction_details = {WRAPPER_REQUIRED: False}
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details
        self.mock_transport.make_request.return_value = sentinel.response

        actual_id, actual_response = self.sender.send_message(sentinel.interaction_name, sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.mock_transport.make_request.assert_called_with(interaction_details, sentinel.message)
        self.assertIsNone(actual_id)
        self.assertIs(sentinel.response, actual_response)

    def test_send_message_incorrect_interaction_name(self):
        self.mock_interactions_config.get_interaction_details.return_value = None

        with (self.assertRaises(UnknownInteractionError)):
            self.sender.send_message("unknown_interaction", "message")
