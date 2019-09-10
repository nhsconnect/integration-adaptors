from unittest import TestCase
from unittest.mock import patch, MagicMock
from exceptions import MaxRetriesExceeded
from mhs_common.state import work_description as wd
from utilities import test_utilities
from mhs_common.workflow import sync_async
from mhs_common import workflow
from mhs_common.workflow import sync_async_resynchroniser as resynchroniser

PARTY_ID = "PARTY-ID"


class TestSyncAsyncWorkflowOutbound(TestCase):

    def setUp(self):
        self.persistence = MagicMock()
        self.work_description = MagicMock()
        self.work_description_store = MagicMock()
        self.resync = MagicMock()
        self.workflow = sync_async.SyncAsyncWorkflow(PARTY_ID,
                                                     work_description_store=self.work_description_store,
                                                     resynchroniser=self.resync,
                                                     persistence_store_max_retries=3)

    @patch('mhs_common.state.work_description.update_status_with_retries')
    @patch('mhs_common.state.work_description.create_new_work_description')
    @test_utilities.async_test
    async def test_sync_async_happy_path(self, wd_mock, update_mock):
        wd_mock.return_value = MagicMock()
        update_mock.return_value = test_utilities.awaitable(True)
        async_workflow = MagicMock()
        self.resync.pause_request.return_value = test_utilities.awaitable({sync_async.MESSAGE_DATA: 'data'})
        result = (202, {})
        async_workflow.handle_outbound_message.return_value = test_utilities.awaitable(result)

        code, body, wdo = await self.workflow.handle_sync_async_outbound_message('id123', 'cor123', {},
                                                                                 'payload',
                                                                                 async_workflow
                                                                                 )

        wd_mock.assert_called_with(self.work_description_store,
                                   'id123',
                                   workflow.SYNC_ASYNC,
                                   outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)

        async_workflow.handle_outbound_message.assert_called_once()
        async_workflow.handle_outbound_message.assert_called_with('id123', 'cor123', {}, 'payload',
                                                                  wd_mock.return_value)
        update_mock.assert_called_with(wd_mock.return_value,
                                       wd_mock.return_value.set_outbound_status,
                                       wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_LOADED,
                                       3)

        self.assertEqual(code, 200)
        self.assertEqual(body, 'data')
        self.assertEqual(wdo, wd_mock.return_value)

    @patch('mhs_common.state.work_description.create_new_work_description')
    @test_utilities.async_test
    async def test_async_workflow_return_error_code(self, wd_mock):
        wd_mock.return_value = MagicMock()
        async_workflow = MagicMock()
        result = (500, "Failed to reach spine")
        async_workflow.handle_outbound_message.return_value = test_utilities.awaitable(result)

        status, response, wdo = await self.workflow.handle_sync_async_outbound_message('id123', 'cor123', {},
                                                                                       'payload',
                                                                                       async_workflow
                                                                                       )
        self.assertEqual(status, 500)
        self.assertEqual("Failed to reach spine", response)

    @test_utilities.async_test
    async def test_resync_failure(self):
        async def resync_raises_exception(fake_key):
            raise resynchroniser.SyncAsyncResponseException()

        with patch('mhs_common.state.work_description.create_new_work_description'):
            async_workflow = MagicMock()

            self.resync.pause_request.side_effect = resync_raises_exception
            result = (202, "Huge success")
            async_workflow.handle_outbound_message.return_value = test_utilities.awaitable(result)

            status, response, wdo = await self.workflow.handle_sync_async_outbound_message('id123', 'cor123', {},
                                                                                           'payload',
                                                                                           async_workflow
                                                                                           )
            self.assertEqual(status, 500)
            self.assertEqual("No async response received from sync-async store", response)


class TestSyncAsyncWorkflowInbound(TestCase):

    def setUp(self):
        self.persistence = MagicMock()
        self.work_description = MagicMock()

        self.workflow = sync_async.SyncAsyncWorkflow(sync_async_store=self.persistence, persistence_store_max_retries=3)

    @test_utilities.async_test
    async def test_inbound_workflow_happy_path(self):
        self.workflow.sync_async_store.add.return_value = test_utilities.awaitable(True)
        self.work_description.set_inbound_status.return_value = test_utilities.awaitable(True)
        self.work_description.update.return_value = test_utilities.awaitable(True)

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
        self.work_description.update.return_value = test_utilities.awaitable(True)

        def add_to_store_mock_throws_exception(key, value):
            raise ValueError('Fake error')

        self.persistence.add.side_effect = add_to_store_mock_throws_exception
        self.work_description.set_inbound_status.return_value = test_utilities.awaitable(True)

        self.workflow = sync_async.SyncAsyncWorkflow(sync_async_store=self.persistence,
                                                     persistence_store_max_retries=3,
                                                     sync_async_store_retry_delay=100)
        with self.assertRaises(MaxRetriesExceeded):
            await self.workflow.handle_inbound_message('1', 'cor_id', self.work_description, 'wqe')

        self.work_description.set_inbound_status.assert_called_with(
            wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED)

        self.assertEqual(self.persistence.add.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(100 / 1000)
