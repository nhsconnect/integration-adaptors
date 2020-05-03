import unittest
from unittest.mock import MagicMock

from outbound.state import work_description as wd

input_data = {
    wd.OPERATION_ID: 'aaa-bbb-ccc',
    wd.DATA: {
        wd.TRANSACTION_ID: 1,
        wd.TRANSACTION_TIMESTAMP: '12:00',
        wd.TRANSACTION_TYPE: 'interchange',
        wd.SIS_SEQUENCE: 2,
        wd.SMS_SEQUENCES: [3, 7],
        wd.SENDER: 'test_sender',
        wd.RECIPIENT: 'test_recipient'
    }
}


class TestWorkDescription(unittest.TestCase):

    def verify_results_for_input_data(self, work_description):
        self.assertEqual(work_description.operation_id, 'aaa-bbb-ccc')
        self.assertEqual(work_description.transaction_id, 1)
        self.assertEqual(work_description.transaction_timestamp, '12:00')
        self.assertEqual(work_description.transaction_type, 'interchange')
        self.assertEqual(work_description.sis_sequence, 2)
        self.assertEqual(work_description.sms_sequences, [3, 7])
        self.assertEqual(work_description.sender, 'test_sender')
        self.assertEqual(work_description.recipient, 'test_recipient')

    def test_constructor(self):
        persistence = MagicMock()
        work_description = wd.WorkDescription(persistence, input_data)

        self.verify_results_for_input_data(work_description)

    def test_create_work_description(self):
        persistence = MagicMock()
        work_description = wd.create_new_work_description(persistence,
                                                          operation_id='aaa-bbb-ccc',
                                                          transaction_id=1,
                                                          transaction_timestamp='12:00',
                                                          transaction_type='interchange',
                                                          sis_sequence=2,
                                                          sms_sequences=[3, 7],
                                                          sender='test_sender',
                                                          recipient='test_recipient'
                                                          )
        self.verify_results_for_input_data(work_description)

    def test_create_wd_none_or_empty_parameters(self):
        persistence = MagicMock()
        with self.subTest('None operation_id'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id=None,
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('Empty operation_id string'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('None transaction_id'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=None,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('None timestamp'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp=None,
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('Empty timestamp string'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('None transaction_type'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type=None,
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('Empty transaction_type string'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('None sis sequence'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=None,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('None sms sequences'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=None,
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('Empty sms sequences list'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[],
                    sender='test_sender',
                    recipient='test_recipient'
                )
        with self.subTest('None sender'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender=None,
                    recipient='test_recipient'
                )
        with self.subTest('Empty sender string'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='',
                    recipient='test_recipient'
                )
        with self.subTest('None recipient'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient=None
                )
        with self.subTest('Empty recipient string'):
            with self.assertRaises(ValueError):
                wd.create_new_work_description(
                    persistence,
                    operation_id='aaa-bbb-ccc',
                    transaction_id=1,
                    transaction_timestamp='12:00',
                    transaction_type='interchange',
                    sis_sequence=2,
                    sms_sequences=[3, 7],
                    sender='test_sender',
                    recipient=''
                )