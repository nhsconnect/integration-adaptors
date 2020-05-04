import re
import unittest
from datetime import datetime, timezone
from unittest import mock

import sequence.sequence_manager
from edifact.outgoing.models.message import ReferenceTransactionType
from outbound.converter.interchange_translator import InterchangeTranslator
from outbound.tests.fhir_test_helpers import create_patient, HA_ID, GP_ID
from utilities.date_utilities import DateUtilities
from utilities.test_utilities import async_test, awaitable


class TestFhirToEdifactTranslator(unittest.TestCase):

    UNB_PATTERN = r"^UNB\+UNOA:2\+(?P<sender>[a-zA-Z0-9]+)\+(?P<recipient>[a-zA-Z0-9]+)+\+(?P<timestamp>[0-9]{6}:[0-9]{4})\+(?P<sis>[0-9]{8})'$"
    UNH_PATTERN = r"^UNH\+(?P<sms>[0-9]{8})\+FHSREG:0:1:FH:FHS001'$"
    BGM_PATTERN = r"^BGM\+\+\+507'$"
    NAD_MSG_HEADER_PATTERN = r"^NAD\+(?P<party_qualifier>FHS)\+(?P<party_id>[A-Z0-9]+):(?P<party_code>954)'$"
    DTM_MSG_HEADER_PATTERN = r"^DTM\+(?P<type_code>137|206):(?P<date_time_value>[0-9]{12}|[0-9]{8}):(?P<format_code>203|102)'$"
    S01_PATTERN = r"^S01\+1'$"
    RFF_TN_PATTERN = r"^RFF\+TN:(?P<transaction_number>[0-9]{1,8})'$"
    UNT_PATTERN = r"^UNT\+(?P<segment_count>[0-9]+)\+(?P<sms>[0-9]{8})'$"
    UNZ_PATTERN = r"^UNZ\+(?P<message_count>[0-9]+)\+(?P<sis>[0-9]{8})'$"

    @mock.patch.object(sequence.sequence_manager.IdGenerator, 'generate_message_id')
    @mock.patch.object(sequence.sequence_manager.IdGenerator, 'generate_interchange_id')
    @mock.patch.object(sequence.sequence_manager.IdGenerator, 'generate_transaction_id')
    @mock.patch('utilities.date_utilities.DateUtilities.utc_now')
    @async_test
    async def test_message_translated(self, mock_utc_now, mock_generate_transaction_id, mock_generate_interchange_id,
                                      mock_generate_message_id):
        expected_date = datetime(year=2020, month=4, day=27, hour=17, minute=37, tzinfo=timezone.utc)
        mock_utc_now.return_value = expected_date
        mock_generate_transaction_id.return_value = awaitable(5174)
        mock_generate_interchange_id.return_value = awaitable(45)
        mock_generate_message_id.return_value = awaitable(56)
        self.assertEqual(expected_date, DateUtilities.utc_now())
        patient = create_patient()

        translator = InterchangeTranslator()
        edifact = await translator.convert(patient, ReferenceTransactionType.TransactionType.ACCEPTANCE)

        self.assertIsNotNone(edifact)
        self.assertTrue(len(edifact) > 0)
        segments = edifact.splitlines()

        unz = segments.pop()
        self.assertRegex(unz, self.UNZ_PATTERN)
        unz_match = re.match(self.UNZ_PATTERN, unz)
        self.assertEqual('1', unz_match.group('message_count'))
        self.assertEqual('00000045', unz_match.group('sis'))

        unt = segments.pop()
        self.assertRegex(unt, self.UNT_PATTERN)
        unt_match = re.match(self.UNT_PATTERN, unt)
        self.assertEqual('7', unt_match.group('segment_count'))
        self.assertEqual('00000056', unt_match.group('sms'))

        rff_tn = segments.pop()
        self.assertRegex(rff_tn, self.RFF_TN_PATTERN)
        rff_tn_match = re.match(self.RFF_TN_PATTERN, rff_tn)
        self.assertEqual('5174', rff_tn_match.group('transaction_number'))

        s01 = segments.pop()
        self.assertRegex(s01, self.S01_PATTERN)

        dtm_msg_header = segments.pop()
        self.assertRegex(dtm_msg_header, self.DTM_MSG_HEADER_PATTERN)
        dtm_msg_header_match = re.match(self.DTM_MSG_HEADER_PATTERN, dtm_msg_header)
        self.assertEqual('137', dtm_msg_header_match.group('type_code'))
        self.assertEqual('202004271737', dtm_msg_header_match.group('date_time_value'))
        self.assertEqual('203', dtm_msg_header_match.group('format_code'))

        nad_msg_header = segments.pop()
        self.assertRegex(nad_msg_header, self.NAD_MSG_HEADER_PATTERN)
        nad_msg_header_match = re.match(self.NAD_MSG_HEADER_PATTERN, nad_msg_header)
        self.assertEqual('FHS', nad_msg_header_match.group('party_qualifier'))
        self.assertEqual(HA_ID, nad_msg_header_match.group('party_id'))
        self.assertEqual('954', nad_msg_header_match.group('party_code'))

        bgm = segments.pop()
        self.assertRegex(bgm, self.BGM_PATTERN)

        unh = segments.pop()
        self.assertRegex(unh, self.UNH_PATTERN)
        unh_match = re.match(self.UNH_PATTERN, unh)
        self.assertEqual('00000056', unh_match.group('sms'))

        unb = segments.pop()
        self.assertRegex(unb, self.UNB_PATTERN)
        unb_match = re.match(self.UNB_PATTERN, unb)
        self.assertEqual(GP_ID, unb_match.group('sender'))
        self.assertEqual(HA_ID, unb_match.group('recipient'))
        self.assertEqual('200427:1737', unb_match.group('timestamp'))
        self.assertEqual('00000045', unb_match.group('sis'))
