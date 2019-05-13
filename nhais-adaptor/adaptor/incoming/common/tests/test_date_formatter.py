import unittest
import adaptor.incoming.common.date_formatter as date_formatter


class TestIncomingDateFormatter(unittest.TestCase):
    def test_format_date_time(self):
        """
        Tests the function that formats the edifact date time stamp to a fhir format
        """
        formatted_date = date_formatter.format_date_time("190501:0902")
        self.assertEqual(formatted_date, "2019-05-01 09:02")
