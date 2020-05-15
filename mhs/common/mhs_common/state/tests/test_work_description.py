import copy
import unittest
from unittest.mock import MagicMock, patch

from mhs_common import workflow
from mhs_common.state import work_description as wd
from utilities import test_utilities
from utilities.test_utilities import async_test

input_data = {
    wd.MESSAGE_ID: 'aaa-aaa-aaa',
    wd.CREATED_TIMESTAMP: '11:59',
    wd.INBOUND_STATUS: None,
    wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
    wd.WORKFLOW: workflow.SYNC
}


old_data = {
    wd.MESSAGE_ID: 'aaa-aaa-aaa',
    wd.CREATED_TIMESTAMP: '11:59',
    wd.INBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
    wd.OUTBOUND_STATUS: None,
    wd.WORKFLOW: workflow.SYNC
}


class TestWorkDescription(unittest.TestCase):

    def test_constructor(self):
        persistence = MagicMock()
        work_description = wd.WorkDescription(persistence, input_data)

        self.assertEqual(work_description.message_id, input_data[wd.MESSAGE_ID])
        self.assertEqual(work_description.workflow, input_data[wd.WORKFLOW])
        self.assertEqual(work_description.inbound_status, input_data[wd.INBOUND_STATUS])
        self.assertEqual(work_description.outbound_status, input_data[wd.OUTBOUND_STATUS])
        self.assertEqual(work_description.created_timestamp, input_data[wd.CREATED_TIMESTAMP])

    @async_test
    async def test_publish_saves_new_data(self):
        future = test_utilities.awaitable(old_data)

        persistence = MagicMock()
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        await work_description.publish()
        persistence.add.assert_called_with(input_data[wd.MESSAGE_ID], input_data)

    @async_test
    async def test_set_outbound_status(self):
        updated_data = copy.deepcopy(input_data)
        updated_data[wd.OUTBOUND_STATUS] = wd.MessageStatus.OUTBOUND_MESSAGE_ACKD

        future = test_utilities.awaitable(updated_data)

        persistence = MagicMock()
        persistence.update.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        await work_description.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
        persistence.update.assert_called_with(input_data[wd.MESSAGE_ID], {wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_ACKD})

        self.assertEqual(work_description.outbound_status, wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)

    @async_test
    async def test_set_inbound_status(self):
        updated_data = copy.deepcopy(input_data)
        updated_data[wd.INBOUND_STATUS] = wd.MessageStatus.INBOUND_RESPONSE_FAILED

        future = test_utilities.awaitable(updated_data)

        persistence = MagicMock()
        persistence.update.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_FAILED)
        persistence.update.assert_called_with(input_data[wd.MESSAGE_ID], {wd.INBOUND_STATUS: wd.MessageStatus.INBOUND_RESPONSE_FAILED})

        self.assertEqual(work_description.inbound_status, wd.MessageStatus.INBOUND_RESPONSE_FAILED)

    def test_null_persistence(self):
        with self.assertRaises(ValueError):
            wd.WorkDescription(None, {'None': 'None'})


class TestWorkDescriptionFactory(unittest.TestCase):

    @patch('mhs_common.state.work_description.WorkDescription')
    @async_test
    async def test_get_from_store(self, work_mock):
        persistence = MagicMock()
        persistence.get.return_value = test_utilities.awaitable(old_data)
        await wd.get_work_description_from_store(persistence, 'aaa-aaa-aaa')

        persistence.get.assert_called_with('aaa-aaa-aaa', strongly_consistent_read=True)
        work_mock.assert_called_with(persistence, old_data)

    @async_test
    async def test_get_from_store_no_result_found(self):
        persistence = MagicMock()
        persistence.get.return_value = test_utilities.awaitable(None)

        self.assertIsNone(await wd.get_work_description_from_store(persistence, 'aaa-aaa-aaa'))

    @async_test
    async def test_get_from_store_empty_store(self):
        with self.assertRaises(ValueError):
            await wd.get_work_description_from_store(None, 'aaa')

    @async_test
    async def test_get_from_store_empty_message_id(self):
        with self.assertRaises(ValueError):
            await wd.get_work_description_from_store(MagicMock(), None)

    @patch('utilities.timing.get_time')
    @patch('mhs_common.state.work_description.WorkDescription')
    def test_create_work_description(self, work_mock, time_mock):
        time_mock.return_value = '12'
        persistence = MagicMock()
        wd.create_new_work_description(persistence,
                                       message_id='aaa-aaa',
                                       outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                                       workflow=workflow.SYNC
                                       )
        work_mock.assert_called_with(
            persistence,
            wd.build_store_data(
                'aaa-aaa',
                '12',
                workflow.SYNC,
                outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED))

    def test_create_wd_null_parameters(self):
        persistence = MagicMock()
        with self.subTest('Null key'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    message_id=None,
                    outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                    workflow=workflow.SYNC
                )
        with self.subTest('Null persistence'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    None,
                    message_id='aaa',
                    outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                    workflow=workflow.SYNC
                )
        with self.subTest('Null workflow'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    message_id='aaa',
                    outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                    workflow=None
                )
        with self.subTest('Null statuses'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    message_id='aaa',
                    outbound_status=None,
                    inbound_status=None,
                    workflow=workflow.SYNC_ASYNC
                )

        with self.subTest('Single null status should not raise error'):
            wd.create_new_work_description(
                persistence,
                message_id='aaa',
                outbound_status=wd.MessageStatus.INBOUND_RESPONSE_FAILED,
                inbound_status=None,
                workflow=workflow.SYNC_ASYNC
            )
