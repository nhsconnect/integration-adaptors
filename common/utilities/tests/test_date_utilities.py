import unittest
from datetime import datetime, timezone, timedelta

import time
from isodate import isoerror

from utilities.date_utilities import DateUtilities


class TestDateUtilities(unittest.TestCase):

    def test_xml_dates_parsed_successfully(self):
        test_cases = [('P1DT2H', 93600),
                      ('PT20M', 1200),
                      ('PT1M30.5S', 90.5),
                      ('PT10S', 10),
                      ('PT1M', 60),
                      ('PT20S', 20),
                      ('PT4M', 240),
                      ('PT1H', 3600)]
        for xml_date, expected_seconds in test_cases:
            description = 'Test {} is parsed to seconds correctly'.format(xml_date)
            with self.subTest(description):
                actual_seconds = DateUtilities.convert_xml_date_time_format_to_seconds(xml_date)
                self.assertEqual(expected_seconds, actual_seconds, 'Should have parsed to expected number of seconds')

    def test_xml_dates_unable_to_parse(self):
        test_cases = [
            ('P', isoerror.ISO8601Error),
            ('PT15.S', isoerror.ISO8601Error),
            ('1Y2M', isoerror.ISO8601Error)
        ]
        for xml_date, expected_exception in test_cases:
            description = 'Test {} is unable to be parsed to seconds correctly'.format(xml_date)
            with self.subTest(description):
                with self.assertRaises(expected_exception):
                    DateUtilities.convert_xml_date_time_format_to_seconds(xml_date)

    def test_utc_now(self):
        past = datetime.now(tz=timezone(timedelta()))  # another way to create a UTC (+00:00) timestamp
        time.sleep(0.1)
        present = DateUtilities.utc_now()
        time.sleep(0.1)
        future = datetime.now(tz=timezone(timedelta()))
        self.assertTrue(past < present)
        self.assertTrue(present < future)
        self.assertEqual(timezone.utc, present.tzinfo, 'datetime from utc_now() should be UTC')
