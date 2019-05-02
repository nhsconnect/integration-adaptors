import unittest
import edifact.helpers.date_formatter as formatter


class TestDateFormatter(unittest.TestCase):
    """
    Tests the formatting of date time to an edifact date time stamp
    """

    def test_format_date_for_qualifier_203(self):
        date_time = "2019-04-23 09:00:04.159338"
        formatted_date = formatter.format_date(date_time=date_time, format_qualifier="203")
        self.assertEqual(formatted_date, "201904230900")

    def test_format_date_for_qualifier_102(self):
        date_time = "2019-04-23 09:00:04.159338"
        formatted_date = formatter.format_date(date_time=date_time, format_qualifier="102")
        self.assertEqual(formatted_date, "20190423")

    def test_format_date_for_qualifier_default(self):
        date_time = "2019-04-23 09:00:04.159338"
        formatted_date = formatter.format_date(date_time=date_time)
        self.assertEqual(formatted_date, "190423:0900")

    def test_format_date_when_current_format_is_not_the_default(self):
        date_time = "2019-04-23"
        formatted_date = formatter.format_date(date_time=date_time, format_qualifier="102", current_format="%Y-%m-%d")
        self.assertEqual(formatted_date, "20190423")
