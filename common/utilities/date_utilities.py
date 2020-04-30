"""
Date utility class
"""
from datetime import datetime, tzinfo, timezone

import isodate


class DateUtilities(object):
    @staticmethod
    def convert_xml_date_time_format_to_seconds(xml_date_time):
        """
        This method converts an xsd_duration (http://www.datypic.com/sc/xsd/t-xsd_duration.html) value into seconds
        :param xml_date_time: a xsd_duration string value
        :return: seconds: the xsd_duration parsed into seconds
        """
        timedelta = isodate.parse_duration(xml_date_time)
        return timedelta.total_seconds()

    @staticmethod
    def utc_now() -> datetime:
        """
        :return: the current datetime in utc
        """
        return datetime.now(tz=timezone.utc)
