import asyncio
import json
import unittest
from unittest.mock import MagicMock, patch

from utilities.test_utilities import async_test

import mhs.common.state.work_description as wd

DEFAULT_TABLE = 'default'


class TestWorkDescription(unittest.TestCase):

    def test_constructor(self):
        wd_input = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.VERSION_KEY: 1,
                wd.TIMESTAMP: '12:00',
                wd.STATUS: wd.MessageStatus.IN_OUTBOUND_WORKFLOW
            }
        }

        persistence = MagicMock()
        work_description = wd.WorkDescription(persistence, DEFAULT_TABLE, wd_input)

        self.assertEqual(work_description.status, wd.MessageStatus.IN_OUTBOUND_WORKFLOW)
        self.assertEqual(work_description.version, 1)
        self.assertEqual(work_description.timestamp, '12:00')

    @async_test
    async def test_publish_updates(self):
        wd_input = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.TIMESTAMP: '12:00',
                wd.VERSION_KEY: 1,
                wd.STATUS: wd.MessageStatus.IN_OUTBOUND_WORKFLOW
            }
        }

        old_value = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.VERSION_KEY: 1,
                wd.TIMESTAMP: '11:00',
                wd.STATUS: wd.MessageStatus.IN_OUTBOUND_WORKFLOW
            }
        }

        future = asyncio.Future()
        future.set_result(old_value)

        persistence = MagicMock()
        persistence.get.return_value = future
        persistence.add.return_value = future
        work_description = wd.WorkDescription(persistence, DEFAULT_TABLE, wd_input)

        await work_description.publish()
        persistence.add.assert_called_with(DEFAULT_TABLE, json.dumps(wd_input))

    @async_test
    async def test_out_of_date_version(self):
        wd_input = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.TIMESTAMP: '12:00',
                wd.VERSION_KEY: 1,
                wd.STATUS: wd.MessageStatus.IN_OUTBOUND_WORKFLOW
            }
        }

        old_value = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.VERSION_KEY: 3,
                wd.TIMESTAMP: '11:00',
                wd.STATUS: wd.MessageStatus.IN_OUTBOUND_WORKFLOW
            }
        }

        future = asyncio.Future()
        future.set_result(old_value)

        persistence = MagicMock()
        persistence.get.return_value = future
        work_description = wd.WorkDescription(persistence, DEFAULT_TABLE, wd_input)

        with self.assertRaises(wd.OutOfDateVersionError):
            await work_description.publish()

    def test_null_persistence(self):
        with self.assertRaises(ValueError):
            wd.WorkDescription(None, DEFAULT_TABLE, {'None': 'None'})

    def test_null_table(self):
        with self.assertRaises(ValueError):
            wd.WorkDescription("q", '', {'None': 'None'})


class TestWorkDescriptionFactory(unittest.TestCase):

    @patch('mhs.common.state.work_description.WorkDescription')
    @async_test
    async def test_get_from_store(self, work_mock):
        old_value = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.VERSION_KEY: 3,
                wd.TIMESTAMP: '11:00',
                wd.STATUS: wd.MessageStatus.IN_OUTBOUND_WORKFLOW
            }
        }

        future = asyncio.Future()
        future.set_result(old_value)

        persistence = MagicMock()
        persistence.get.return_value = future
        await wd.WorkDescriptionFactory.get_work_description_from_store(persistence, DEFAULT_TABLE, 'aaa-aaa-aaa')

        persistence.get.assert_called_with(DEFAULT_TABLE, 'aaa-aaa-aaa')
        work_mock.assert_called_with(persistence, DEFAULT_TABLE, old_value)

    @async_test
    async def test_get_from_store_empty_store(self):
        with self.assertRaises(ValueError):
            await wd.WorkDescriptionFactory.get_work_description_from_store(None, DEFAULT_TABLE, 'aaa')

    @async_test
    async def test_get_from_store_empty_message_id(self):
        with self.assertRaises(ValueError):
            await wd.WorkDescriptionFactory.get_work_description_from_store(MagicMock(), DEFAULT_TABLE, None)

    @patch('mhs.common.state.work_description.WorkDescription')
    def test_create_work_description(self, work_mock):
        persistence = MagicMock()
        wd.WorkDescriptionFactory.create_new_work_description(persistence,
                                                              DEFAULT_TABLE,
                                                              key='aaa-aaa',
                                                              status=wd.MessageStatus.RECEIVED,
                                                              timestamp='12:00.11')
        work_mock.assert_called_with(
            persistence,
            DEFAULT_TABLE,
            {
                wd.DATA_KEY: 'aaa-aaa',
                wd.DATA: {
                    wd.TIMESTAMP: '12:00.11',
                    wd.STATUS: wd.MessageStatus.RECEIVED,
                    wd.VERSION_KEY: 1
                }

            })

    def test_create_wd_null_parameters(self):
        persistence = MagicMock()
        with self.subTest('Null key'):
            with self.assertRaises(ValueError):
                wd.WorkDescriptionFactory.create_new_work_description(
                    persistence,
                    table_name=DEFAULT_TABLE,
                    key=None,
                    timestamp='12',
                    status=wd.MessageStatus.RECEIVED
                )

        with self.subTest('Null timestamp'):
            with self.assertRaises(ValueError):
                wd.WorkDescriptionFactory.create_new_work_description(
                    persistence,
                    table_name=DEFAULT_TABLE,
                    key='aaa',
                    timestamp=None,
                    status=wd.MessageStatus.RECEIVED
                )

        with self.subTest('Null status'):
            with self.assertRaises(ValueError):
                wd.WorkDescriptionFactory.create_new_work_description(
                    persistence,
                    table_name=DEFAULT_TABLE,
                    key='aaa',
                    timestamp='12',
                    status=None
                )
