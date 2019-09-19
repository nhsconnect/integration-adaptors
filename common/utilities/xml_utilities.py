import unittest

import isodate
from lxml import etree
from lxml import objectify


class XmlUtilities(object):

    @staticmethod
    def assert_xml_equal(expected, actual):
        """
        Given two strings of xml this method normalises them and asserts they are equal
        :param expected:
        :param actual:
        """
        obj1 = objectify.fromstring(expected)
        expected = etree.tostring(obj1)
        obj2 = objectify.fromstring(actual)
        actual = etree.tostring(obj2)

        unittest.TestCase().assertEqual(expected, actual)

    @staticmethod
    def assert_xml_equal_utf_8(expected, actual):
        """
        This method ensures the two strings are both in utf encoding for when the default `assert_xml_equal`
        fails due to encoding issues
        :param expected:
        :param actual:
        """
        expected = expected.encode('utf-8')
        actual = actual.encode('utf-8')
        parser = etree.XMLParser(encoding='utf-8')

        obj1 = objectify.fromstring(expected, parser=parser)
        expected = etree.tostring(obj1)
        obj2 = objectify.fromstring(actual, parser=parser)
        actual = etree.tostring(obj2)

        unittest.TestCase().assertEqual(expected, actual)

    @staticmethod
    def convert_xml_date_time_format_to_seconds(xml_date_time):
        """
        This method converts an xsd_duration (http://www.datypic.com/sc/xsd/t-xsd_duration.html) value into seconds
        :param xml_date_time: a xsd_duration string value
        :return: seconds: the xsd_duration parsed into seconds
        """
        timedelta = isodate.parse_duration(xml_date_time)
        return timedelta.total_seconds()
