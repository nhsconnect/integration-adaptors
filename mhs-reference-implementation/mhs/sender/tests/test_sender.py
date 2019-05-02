from unittest import TestCase
from unittest.mock import Mock, sentinel

from mhs.sender.sender import Sender

WRAPPER_REQUIRED = "ebxml_wrapper_required"
FROM_PARTY_ID = "from_party_id"
EXPECTED_PARTY_ID = "A91424-9199121"
MESSAGE = "hl7_message"


class TestSender(TestCase):
    def setUp(self):
        self.mock_interactions_config = Mock()
        self.mock_message_builder = Mock()
        self.mock_transport = Mock()

        self.sender = Sender(self.mock_interactions_config, self.mock_message_builder, self.mock_transport)

    def test_send_message_with_ebxml_wrapper(self):
        interaction_details = {WRAPPER_REQUIRED: True}
        expected_context = {
            WRAPPER_REQUIRED: True,
            FROM_PARTY_ID: EXPECTED_PARTY_ID,
            MESSAGE: sentinel.message
        }
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details
        self.mock_message_builder.build_message.return_value = sentinel.ebxml_message
        self.mock_transport.make_request.return_value = sentinel.response

        actual_response = self.sender.send_message(sentinel.interaction_name, sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.mock_message_builder.build_message.assert_called_with(expected_context)
        self.mock_transport.make_request.assert_called_with(interaction_details, sentinel.ebxml_message)
        self.assertIs(sentinel.response, actual_response)

    def test_send_message_without_ebxml_wrapper(self):
        interaction_details = {WRAPPER_REQUIRED: False}
        self.mock_interactions_config.get_interaction_details.return_value = interaction_details
        self.mock_transport.make_request.return_value = sentinel.response

        actual_response = self.sender.send_message(sentinel.interaction_name, sentinel.message)

        self.mock_interactions_config.get_interaction_details.assert_called_with(sentinel.interaction_name)
        self.mock_transport.make_request.assert_called_with(interaction_details, sentinel.message)
        self.assertIs(sentinel.response, actual_response)
