import json
import unittest
from unittest.mock import MagicMock, patch

import mhs.common.state.work_description as wd


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
        work_description = wd.WorkDescription(persistence, wd_input)

        self.assertEqual(work_description.status, wd.MessageStatus.IN_OUTBOUND_WORKFLOW)
        self.assertEqual(work_description.version, 1)
        self.assertEqual(work_description.timestamp, '12:00')

    def test_publish_updates(self):
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

        persistence = MagicMock()
        persistence.get.return_value = old_value
        work_description = wd.WorkDescription(persistence, wd_input)

        work_description.publish()
        persistence.add.assert_called_with('default_table', json.dumps(wd_input))

    def test_out_of_date_version(self):
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

        persistence = MagicMock()
        persistence.get.return_value = old_value
        work_description = wd.WorkDescription(persistence, wd_input)

        with self.assertRaises(wd.OutOfDateVersionError):
            work_description.publish()

    def test_null_persistence(self):
        with self.assertRaises(ValueError):
            wd.WorkDescription(None, {'None': 'None'})


class TestWorkDescriptionFactory(unittest.TestCase):

    @patch('mhs.common.state.work_description.WorkDescription')
    def test_get_from_store(self, work_mock):
        old_value = {
            wd.DATA_KEY: 'aaa-aaa-aaa',
            wd.DATA: {
                wd.VERSION_KEY: 3,
                wd.TIMESTAMP: '11:00',
                wd.STATUS: wd.MessageStatus.IN_OUTBOUND_WORKFLOW
            }
        }

        persistence = MagicMock()
        persistence.get.return_value = old_value
        wd.WorkDescriptionFactory.get_work_description_from_store(persistence, 'aaa-aaa-aaa')

        persistence.get.assert_called_with('default_table', 'aaa-aaa-aaa')
        work_mock.assert_called_with(persistence, old_value)

    def test_get_from_store_empty_store(self):
        with self.assertRaises(ValueError):
            wd.WorkDescriptionFactory.get_work_description_from_store(None, 'aaa')

    def test_get_from_store_empty_message_id(self):
        with self.assertRaises(ValueError):
            wd.WorkDescriptionFactory.get_work_description_from_store(MagicMock(), None)

    @patch('mhs.common.state.work_description.WorkDescription')
    def test_create_work_description(self, work_mock):
        persistence = MagicMock()
        wd.WorkDescriptionFactory.create_new_work_description(persistence,
                                                              key='aaa-aaa',
                                                              status=wd.MessageStatus.RECEIVED,
                                                              timestamp='12:00.11')
        work_mock.assert_called_with(
            persistence,
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
                    key=None,
                    timestamp='12',
                    status=wd.MessageStatus.RECEIVED
                )

        with self.subTest('Null timestamp'):
            with self.assertRaises(ValueError):
                wd.WorkDescriptionFactory.create_new_work_description(
                    persistence,
                    key='aaa',
                    timestamp=None,
                    status=wd.MessageStatus.RECEIVED
                )

        with self.subTest('Null status'):
            with self.assertRaises(ValueError):
                wd.WorkDescriptionFactory.create_new_work_description(
                    persistence,
                    key='aaa',
                    timestamp='12',
                    status=None
                )
