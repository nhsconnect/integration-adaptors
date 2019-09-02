from unittest import TestCase
from unittest.mock import Mock, sentinel, patch, MagicMock
from exceptions import MaxRetriesExceeded
from mhs_common.state import work_description as wd
from utilities import test_utilities
from mhs_common.workflow import sync_async

PARTY_ID = "PARTY-ID"


class TestSyncAsyncWorkflowOutbound(TestCase):

    def setUp(self):
        self.persistence = MagicMock()
        self.work_description = MagicMock()

        self.workflow = sync_async.SyncAsyncWorkflow(PARTY_ID, transmission=None, sync_async_store=self.persistence,
                                                     work_description_store=MagicMock())

    @test_utilities.async_test
    async def test_outbound_happy_path(self):
        workflow = MagicMock()
        await self.workflow.handle_sync_async_outbound_message('id123', 'cor123', {},
                                                               'payload',
                                                               workflow
                                                               )


class TestSyncAsyncWorkflowInbound(TestCase):

    def setUp(self):
        self.persistence = MagicMock()
        self.work_description = MagicMock()

        self.workflow = sync_async.SyncAsyncWorkflow(PARTY_ID, transmission=None, sync_async_store=self.persistence)

    @test_utilities.async_test
    async def test_inbound_workflow_happy_path(self):
        self.workflow.sync_async_store.add.return_value = test_utilities.awaitable(True)
        self.work_description.set_status.return_value = test_utilities.awaitable(True)

        await self.workflow.handle_inbound_message('1', 'cor_id', self.work_description, 'wqe')

        self.persistence.add.assert_called_with('1', {
            'correlation_id': 'cor_id',
            'data': 'wqe'
        })

        self.work_description.set_status.assert_called_with(wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_STORED)

    @patch('asyncio.sleep')
    @test_utilities.async_test
    async def test_inbound_workflow_exception_in_store_retries(self, mock_sleep):
        mock_sleep.return_value = test_utilities.awaitable(None)

        def add_to_store_mock_throws_exception(key, value):
            raise ValueError('Fake error')

        self.persistence.add.side_effect = add_to_store_mock_throws_exception
        self.work_description.set_status.return_value = test_utilities.awaitable(True)

        self.workflow = sync_async.SyncAsyncWorkflow(PARTY_ID, transmission=None,
                                                     sync_async_store=self.persistence,
                                                     sync_async_store_max_retries=3,
                                                     sync_async_store_retry_delay=100)
        with self.assertRaises(MaxRetriesExceeded):
            await self.workflow.handle_inbound_message('1', 'cor_id', self.work_description, 'wqe')

        self.work_description.set_status.assert_called_with(
            wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED)

        self.assertEqual(self.persistence.add.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(100 / 1000)
