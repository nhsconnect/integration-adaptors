import copy
import unittest
from unittest.mock import MagicMock, patch

from utilities import test_utilities
from utilities.test_utilities import async_test

from mhs_common import workflow
from mhs_common.state import work_description as wd

input_data = {
    wd.DATA_KEY: 'aaa-aaa-aaa',
    wd.DATA: {
        wd.CREATED_TIMESTAMP: '11:59',
        wd.LATEST_TIMESTAMP: '12:00',
        wd.VERSION_KEY: 1,
        wd.INBOUND_STATUS: None,
        wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED,
        wd.WORKFLOW: workflow.SYNC
    }
}

old_data = {
    wd.DATA_KEY: 'aaa-aaa-aaa',
    wd.DATA: {
        wd.VERSION_KEY: 0,
        wd.CREATED_TIMESTAMP: '11:59',
        wd.LATEST_TIMESTAMP: '12:00',
        wd.INBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED,
        wd.OUTBOUND_STATUS: None,
        wd.WORKFLOW: workflow.SYNC
    }
}


class TestWorkDescription(unittest.TestCase):

    def test_constructor(self):
        persistence = MagicMock()
        work_description = wd.WorkDescription(persistence, input_data)

        self.assertEqual(work_description.outbound_status, wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED)
        self.assertEqual(work_description.version, 1)
        self.assertEqual(work_description.created_timestamp, '11:59')
        self.assertEqual(work_description.last_modified_timestamp, '12:00')

    @patch('utilities.timing.get_time')
    @async_test
    async def test_publish_updates(self, time_mock):
        time_mock.return_value = '12:00'
        future = test_utilities.awaitable(old_data)

        persistence = MagicMock()
        persistence.get.return_value = future
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        await work_description.publish()
        persistence.add.assert_called_with(input_data[wd.DATA_KEY], input_data)

    @patch('utilities.timing.get_time')
    @async_test
    async def test_publish_update_latest_is_none(self, time_mock):
        time_mock.return_value = '12:00'
        future = test_utilities.awaitable(None)

        persistence = MagicMock()
        persistence.get.return_value = future
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        await work_description.publish()
        persistence.add.assert_called_with(input_data[wd.DATA_KEY], input_data)

    @async_test
    async def test_out_of_date_version(self):
        future = test_utilities.awaitable({
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.VERSION_KEY: 3,
                wd.LATEST_TIMESTAMP: '11:00',
                wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED
            }
        })

        persistence = MagicMock()
        persistence.get.return_value = future
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        with self.assertRaises(wd.OutOfDateVersionError):
            await work_description.publish()

    @patch('utilities.timing.get_time')
    @async_test
    async def test_auto_increase_version(self, time_mock):
        time_mock.return_value = '12:00'
        future = test_utilities.awaitable({
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.VERSION_KEY: 1,
                wd.LATEST_TIMESTAMP: '11:00',
                wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED,
            }
        })

        persistence = MagicMock()
        persistence.get.return_value = future
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)
        await work_description.publish()

        updated = copy.deepcopy(input_data)
        updated[wd.DATA][wd.VERSION_KEY] = 2

        # Check local version updated
        self.assertEqual(work_description.version, 2)
        persistence.add.assert_called_with('aaa-aaa-aaa', updated)

    @patch('utilities.timing.get_time')
    @async_test
    async def test_set_outbound_status(self, time_mock):
        time_mock.return_value = '12:00'
        future = test_utilities.awaitable(old_data)

        persistence = MagicMock()
        persistence.get.return_value = future
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        new_data = copy.deepcopy(input_data)
        new_data[wd.DATA][wd.OUTBOUND_STATUS] = wd.MessageStatus.OUTBOUND_MESSAGE_ACKD

        await work_description.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
        persistence.add.assert_called_with(input_data[wd.DATA_KEY], new_data)

    @patch('utilities.timing.get_time')
    @async_test
    async def test_set_inbound_status(self, time_mock):
        time_mock.return_value = '12:00'
        future = test_utilities.awaitable(old_data)

        persistence = MagicMock()
        persistence.get.return_value = future
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        new_data = copy.deepcopy(input_data)
        new_data[wd.DATA][wd.INBOUND_STATUS] = wd.MessageStatus.INBOUND_RESPONSE_FAILED

        await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_FAILED)
        persistence.add.assert_called_with(input_data[wd.DATA_KEY], new_data)

    def test_null_persistence(self):
        with self.assertRaises(ValueError):
            wd.WorkDescription(None, {'None': 'None'})

    @async_test
    async def test_update_status(self):
        new_data = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.CREATED_TIMESTAMP: '11:59',
                wd.LATEST_TIMESTAMP: '13:00',
                wd.VERSION_KEY: 1,
                wd.INBOUND_STATUS: None,
                wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                wd.WORKFLOW: workflow.SYNC
            }
        }
        persistence = MagicMock()
        persistence.get.return_value = test_utilities.awaitable(new_data)
        work_description = wd.WorkDescription(persistence, old_data)

        await work_description.update()

        self.assertEqual(work_description.version, 1)
        self.assertEqual(work_description.outbound_status, wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
        self.assertEqual(work_description.last_modified_timestamp, '13:00')

    @async_test
    async def test_update_status_no_data_returned(self):
        persistence = MagicMock()
        persistence.get.return_value = test_utilities.awaitable(None)
        work_description = wd.WorkDescription(persistence, old_data)

        with self.assertRaises(wd.EmptyWorkDescriptionError):
            await work_description.update()

    @async_test
    async def test_deserialize(self):
        new_data = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.CREATED_TIMESTAMP: '12:00',
                wd.LATEST_TIMESTAMP: '13:00',
                wd.VERSION_KEY: 1,
                wd.INBOUND_STATUS: wd.MessageStatus.INBOUND_RESPONSE_FAILED,
                wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                wd.WORKFLOW: workflow.SYNC_ASYNC
            }
        }

        work_description = wd.WorkDescription(MagicMock(), old_data)
        work_description._deserialize_data(new_data)

        self.assertEqual(work_description.version, 1)
        self.assertEqual(work_description.created_timestamp, '12:00')
        self.assertEqual(work_description.last_modified_timestamp, '13:00')
        self.assertEqual(work_description.inbound_status, wd.MessageStatus.INBOUND_RESPONSE_FAILED)
        self.assertEqual(work_description.outbound_status, wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
        self.assertEqual(work_description.workflow, workflow.SYNC_ASYNC)


class TestWorkDescriptionFactory(unittest.TestCase):

    @patch('mhs_common.state.work_description.WorkDescription')
    @async_test
    async def test_get_from_store(self, work_mock):
        persistence = MagicMock()
        persistence.get.return_value = test_utilities.awaitable(old_data)
        await wd.get_work_description_from_store(persistence, 'aaa-aaa-aaa')

        persistence.get.assert_called_with('aaa-aaa-aaa')
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
                                       key='aaa-aaa',
                                       outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                                       workflow=workflow.SYNC
                                       )
        work_mock.assert_called_with(
            persistence,
            {
                wd.DATA_KEY: 'aaa-aaa',
                wd.DATA: {
                    wd.CREATED_TIMESTAMP: '12',
                    wd.LATEST_TIMESTAMP: '12',
                    wd.INBOUND_STATUS: None,
                    wd.OUTBOUND_STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                    wd.VERSION_KEY: 1,
                    wd.WORKFLOW: workflow.SYNC
                }
            })

    def test_create_wd_null_parameters(self):
        persistence = MagicMock()
        with self.subTest('Null key'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    key=None,
                    outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                    workflow=workflow.SYNC
                )
        with self.subTest('Null persistence'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    None,
                    key='aaa',
                    outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                    workflow=workflow.SYNC
                )
        with self.subTest('Null workflow'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    key='aaa',
                    outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                    workflow=None
                )
        with self.subTest('Null statuses'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    key='aaa',
                    outbound_status=None,
                    inbound_status=None,
                    workflow=workflow.SYNC_ASYNC
                )

        with self.subTest('Single null status should not raise error'):
            wd.create_new_work_description(
                persistence,
                key='aaa',
                outbound_status=wd.MessageStatus.INBOUND_RESPONSE_FAILED,
                inbound_status=None,
                workflow=workflow.SYNC_ASYNC
            )


class TestWorkDescriptionStatusUpdateRetry(unittest.TestCase):

    @test_utilities.async_test
    async def test_update_success(self):
        wdo = MagicMock()
        wdo.update.return_value = test_utilities.awaitable(True)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        await wd.update_status_with_retries(wdo, wdo.set_outbound_status,
                                            wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                                            20)
        self.assertEqual(wdo.update.call_count, 1)
        self.assertEqual(wdo.set_outbound_status.call_count, 1)

    @test_utilities.async_test
    async def test_should_try_updating_outbound_status_expected_number_of_times(self):
        wdo = MagicMock()
        wdo.update.return_value = test_utilities.awaitable(True)
        wdo.set_outbound_status.side_effect = wd.OutOfDateVersionError
        with self.assertRaises(wd.OutOfDateVersionError):
            await wd.update_status_with_retries(wdo, wdo.set_outbound_status,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                                                20)

        self.assertEqual(wdo.update.call_count, 21)
        self.assertEqual(wdo.set_outbound_status.call_count, 21)

    @test_utilities.async_test
    async def test_should_try_updating_outbound_status_twice_if_retries_set_to_one(self):
        wdo = MagicMock()
        wdo.update.return_value = test_utilities.awaitable(True)
        wdo.set_outbound_status.side_effect = wd.OutOfDateVersionError
        with self.assertRaises(wd.OutOfDateVersionError):
            await wd.update_status_with_retries(wdo, wdo.set_outbound_status,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                                                1)

        self.assertEqual(wdo.update.call_count, 2)
        self.assertEqual(wdo.set_outbound_status.call_count, 2)
