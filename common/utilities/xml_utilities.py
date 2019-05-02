import unittest

from lxml import etree
from lxml import objectify


class XmlUtilities:

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
