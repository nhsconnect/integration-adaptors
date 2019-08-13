from unittest import TestCase
from unittest.mock import Mock, sentinel, patch

import utilities.message_utilities as message_utilities

import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.ebxml_request_envelope as ebxml_request_envelope
import mhs.common.workflow.common as common_workflow
import mhs.common.workflow.sync_async as sync_async

PARTY_ID = "PARTY-ID"
MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"


class TestSyncAsyncWorkflow(TestCase):
    def setUp(self):
        self.mock_transmission = Mock()

        self.workflow = sync_async.SyncAsyncWorkflow(self.mock_transmission, PARTY_ID)

    @patch("mhs.common.messages.ebxml_request_envelope.EbxmlRequestEnvelope")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_prepare_message_async(self, mock_get_uuid, mock_envelope):
        mock_get_uuid.return_value = MOCK_UUID
        expected_context = {
            ebxml_envelope.MESSAGE_ID: sentinel.message_id,
            sync_async.ASYNC_RESPONSE_EXPECTED: True,
            ebxml_envelope.FROM_PARTY_ID: PARTY_ID,
            ebxml_envelope.CONVERSATION_ID: MOCK_UUID,
            ebxml_request_envelope.MESSAGE: sentinel.message
        }
        interaction_details = {sync_async.ASYNC_RESPONSE_EXPECTED: True}
        mock_envelope.return_value.serialize.return_value = \
            sentinel.ebxml_id, sentinel.http_headers, sentinel.ebxml_message

        is_async, actual_response = self.workflow.prepare_message(interaction_details,
                                                                  sentinel.message,
                                                                  sentinel.message_id)

        mock_envelope.assert_called_with(expected_context)
        self.assertTrue(mock_envelope.return_value.serialize.called)
        self.assertTrue(is_async)
        self.assertIs(sentinel.ebxml_message, actual_response)

    def test_prepare_message_sync(self):
        interaction_details = {sync_async.ASYNC_RESPONSE_EXPECTED: False}

        is_async, actual_response = self.workflow.prepare_message(interaction_details,
                                                                  sentinel.message,
                                                                  sentinel.message_id)

        self.assertFalse(is_async)
        self.assertIs(sentinel.message, actual_response)

    def test_send_message(self):
        self.mock_transmission.make_request.return_value = sentinel.response

        actual_response = self.workflow.send_message(sentinel.interaction_details, sentinel.message)

        self.mock_transmission.make_request.assert_called_with(sentinel.interaction_details, sentinel.message)
        self.assertIs(sentinel.response, actual_response)
