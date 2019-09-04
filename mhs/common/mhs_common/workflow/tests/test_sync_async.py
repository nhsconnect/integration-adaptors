from unittest import TestCase
from unittest.mock import Mock, sentinel, patch, MagicMock
import utilities.message_utilities as message_utilities
from exceptions import MaxRetriesExceeded

import mhs_common.messages.ebxml_envelope as ebxml_envelope
import mhs_common.messages.ebxml_request_envelope as ebxml_request_envelope
from mhs_common.workflow import sync_async
from mhs_common.state import work_description as wd
from utilities import test_utilities

PARTY_ID = "PARTY-ID"
MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"


class TestSyncAsyncWorkflow(TestCase):
    
    def setUp(self):
        self.mock_transmission = Mock()

        self.workflow = sync_async.SyncAsyncWorkflow(PARTY_ID, self.mock_transmission)

    @patch("mhs_common.messages.ebxml_request_envelope.EbxmlRequestEnvelope")
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


class TestSyncAsyncWorkflowInbound(TestCase):

    def setUp(self):
        self.persistence = MagicMock()
        self.work_description = MagicMock()

        self.workflow = sync_async.SyncAsyncWorkflow(PARTY_ID, transmission=None, sync_async_store=self.persistence)

    @test_utilities.async_test
    async def test_inbound_workflow_happy_path(self):
        self.workflow.sync_async_store.add.return_value = test_utilities.awaitable(True)
        self.work_description.set_inbound_status.return_value = test_utilities.awaitable(True)

        await self.workflow.handle_inbound_message('1', 'cor_id', self.work_description, 'wqe')
        
        self.persistence.add.assert_called_with('1', {
            'correlation_id': 'cor_id',
            'data': 'wqe'
        })
        
        self.work_description.set_inbound_status.assert_called_with(wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_STORED)

    @patch('asyncio.sleep')
    @test_utilities.async_test
    async def test_inbound_workflow_exception_in_store_retries(self, mock_sleep):
        mock_sleep.return_value = test_utilities.awaitable(None)

        def add_to_store_mock_throws_exception(key, value):
            raise ValueError('Fake error')

        self.persistence.add.side_effect = add_to_store_mock_throws_exception
        self.work_description.set_inbound_status.return_value = test_utilities.awaitable(True)

        self.workflow = sync_async.SyncAsyncWorkflow(PARTY_ID, transmission=None,
                                                     sync_async_store=self.persistence,
                                                     sync_async_store_max_retries=3,
                                                     sync_async_store_retry_delay=100)
        with self.assertRaises(MaxRetriesExceeded):
            await self.workflow.handle_inbound_message('1', 'cor_id', self.work_description, 'wqe')

        self.work_description.set_inbound_status.assert_called_with(
            wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED)

        self.assertEqual(self.persistence.add.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(100/1000)





