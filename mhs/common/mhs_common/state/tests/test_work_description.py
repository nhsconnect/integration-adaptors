import copy
import json
import unittest
from mhs_common.state import work_description as wd
from unittest.mock import MagicMock, patch
from utilities import test_utilities
from utilities.test_utilities import async_test

input_data = {
    wd.DATA_KEY: 'aaa-aaa-aaa',
    wd.DATA: {
        wd.CREATED_TIMESTAMP: '11:59',
        wd.LATEST_TIMESTAMP: '12:00',
        wd.VERSION_KEY: 1,
        wd.STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED
    }
}

old_data = {
    wd.DATA_KEY: 'aaa-aaa-aaa',
    wd.DATA: {
        wd.VERSION_KEY: 0,
        wd.CREATED_TIMESTAMP: '11:59',
        wd.LATEST_TIMESTAMP: '12:00',
        wd.STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED
    }
}


class TestWorkDescription(unittest.TestCase):

    def test_constructor(self):
        persistence = MagicMock()
        work_description = wd.WorkDescription(persistence, input_data)

        self.assertEqual(work_description.status, wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED)
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
        persistence.add.assert_called_with(input_data[wd.DATA_KEY], json.dumps(input_data))

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
        persistence.add.assert_called_with(input_data[wd.DATA_KEY], json.dumps(input_data))

    @async_test
    async def test_out_of_date_version(self):
        future = test_utilities.awaitable({
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.VERSION_KEY: 3,
                wd.LATEST_TIMESTAMP: '11:00',
                wd.STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED
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
                wd.STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED
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
        persistence.add.assert_called_with('aaa-aaa-aaa', json.dumps(updated))

    @patch('utilities.timing.get_time')
    @async_test
    async def test_set_status(self, time_mock):
        time_mock.return_value = '12:00'
        future = test_utilities.awaitable(old_data)

        persistence = MagicMock()
        persistence.get.return_value = future
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, input_data)

        new_data = copy.deepcopy(input_data)
        new_data[wd.DATA][wd.STATUS] = wd.MessageStatus.OUTBOUND_MESSAGE_ACKD

        await work_description.set_status(wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
        persistence.add.assert_called_with(input_data[wd.DATA_KEY], json.dumps(new_data))

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

        persistence.get.assert_called_with('aaa-aaa-aaa')
        work_mock.assert_called_with(persistence, old_data)

    @async_test
    async def test_get_from_store_no_result_found(self):
        persistence = MagicMock()
        persistence.get.return_value = test_utilities.awaitable(None)

        with self.assertRaises(wd.EmptyWorkDescriptionError):
            await wd.get_work_description_from_store(persistence, 'aaa-aaa-aaa')

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
                                       status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)
        work_mock.assert_called_with(
            persistence,
            {
                wd.DATA_KEY: 'aaa-aaa',
                wd.DATA: {
                    wd.CREATED_TIMESTAMP: '12',
                    wd.LATEST_TIMESTAMP: '12',
                    wd.STATUS: wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                    wd.VERSION_KEY: 1
                }
            })

    def test_create_wd_null_parameters(self):
        persistence = MagicMock()
        with self.subTest('Null key'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    key=None,
                    status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED
                )
        with self.subTest('Null status'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    key='aaa',
                    status=None
                )
        with self.subTest('Null persistence'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    None,
                    key='aaa',
                    status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED
                )
