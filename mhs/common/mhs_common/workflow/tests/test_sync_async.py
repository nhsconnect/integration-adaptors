from unittest import TestCase
from unittest.mock import patch, MagicMock

from mhs_common import workflow
from mhs_common.state import work_description as wd
from mhs_common.workflow import sync_async
from mhs_common.workflow import sync_async_resynchroniser as resynchroniser
from mhs_common.workflow.common import MessageData
from utilities import test_utilities


class TestSyncAsyncWorkflowOutbound(TestCase):

    def setUp(self):
        self.persistence = MagicMock()
        self.work_description = MagicMock()
        self.work_description_store = MagicMock()
        self.resync = MagicMock()
        self.workflow = sync_async.SyncAsyncWorkflow(work_description_store=self.work_description_store,
                                                     resynchroniser=self.resync)

    @patch('mhs_common.state.work_description.create_new_work_description')
    @test_utilities.async_test
    async def test_sync_async_happy_path(self, wd_mock):
        wdo = MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        wd_mock.return_value = wdo

        async_workflow = MagicMock()
        self.resync.pause_request.return_value = test_utilities.awaitable({sync_async.MESSAGE_DATA: 'data'})
        result = (202, {}, None)
        async_workflow.handle_outbound_message.return_value = test_utilities.awaitable(result)

        code, body, actual_wdo = await self.workflow.handle_sync_async_outbound_message(None, 'id123', 'cor123', {},
                                                                                        'payload',
                                                                                        async_workflow)

        wd_mock.assert_called_with(self.work_description_store,
                                   'id123',
                                   workflow.SYNC_ASYNC,
                                   outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)

        async_workflow.handle_outbound_message.assert_called_once()
        async_workflow.handle_outbound_message.assert_called_with(None, 'id123', 'cor123', {}, 'payload',
                                                                  wd_mock.return_value)

        self.assertEqual(code, 200)
        self.assertEqual(body, 'data')
        self.assertEqual(actual_wdo, wdo)

    @patch('mhs_common.state.work_description.create_new_work_description')
    @test_utilities.async_test
    async def test_async_workflow_return_error_code(self, wd_mock):
        wdo = MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        wd_mock.return_value = wdo
        async_workflow = MagicMock()
        result = (500, "Failed to reach spine", None)
        async_workflow.handle_outbound_message.return_value = test_utilities.awaitable(result)

        status, response, _ = await self.workflow.handle_sync_async_outbound_message(None, 'id123', 'cor123', {},
                                                                                     'payload',
                                                                                     async_workflow)
        self.assertEqual(status, 500)
        self.assertEqual("Failed to reach spine", response)

    @patch('mhs_common.state.work_description.create_new_work_description')
    @test_utilities.async_test
    async def test_resync_failure(self, wd_mock):
        async def resync_raises_exception(fake_key):
            raise resynchroniser.SyncAsyncResponseException()

        wdo = MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        wd_mock.return_value = wdo

        async_workflow = MagicMock()

        self.resync.pause_request.side_effect = resync_raises_exception
        result = (202, "Huge success", None)
        async_workflow.handle_outbound_message.return_value = test_utilities.awaitable(result)

        status, response, wdo = await self.workflow.handle_sync_async_outbound_message(None, 'id123', 'cor123', {},
                                                                                       'payload',
                                                                                       async_workflow)
        self.assertEqual(status, 500)
        self.assertEqual("No async response received from sync-async store", response)

    @test_utilities.async_test
    async def test_success_response(self):
        wdo = MagicMock()
        wdo.update.return_value = test_utilities.awaitable(None)
        wdo.publish.return_value = test_utilities.awaitable(None)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        await self.workflow.set_successful_message_response(wdo)
        wdo.set_outbound_status.assert_called_once_with(
            wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED)

    @test_utilities.async_test
    async def test_failure_response(self):
        wdo = MagicMock()
        wdo.update.return_value = test_utilities.awaitable(None)
        wdo.publish.return_value = test_utilities.awaitable(None)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        await self.workflow.set_failure_message_response(wdo)
        wdo.set_outbound_status.assert_called_once_with(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND)


class TestSyncAsyncWorkflowInbound(TestCase):

    message_data = MessageData(None, 'wqe', None)

    def setUp(self):
        self.persistence = MagicMock()
        self.work_description = MagicMock()

        self.workflow = sync_async.SyncAsyncWorkflow(sync_async_store=self.persistence)

    @test_utilities.async_test
    async def test_inbound_workflow_happy_path(self):
        self.workflow.sync_async_store.add.return_value = test_utilities.awaitable(True)
        self.work_description.set_inbound_status.return_value = test_utilities.awaitable(True)
        self.work_description.update.return_value = test_utilities.awaitable(True)

        await self.workflow.handle_inbound_message('1', 'cor_id', self.work_description, self.message_data)

        self.persistence.add.assert_called_with('1', {
            'MESSAGE_ID': '1',
            'CORRELATION_ID': 'cor_id',
            'DATA': 'wqe'
        })

        self.work_description.set_inbound_status.assert_called_with(wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_STORED)
