
from lxml import etree
from lxml import objectify
import unittest


class Utils:

    @staticmethod
    def assert_xml_equal(expected, actual):
        """
        Given two strings of xml this method normalises them and asserts they are equal
        :param expected:
        :param actual:
        :return:
        """
        obj1 = objectify.fromstring(expected)
        expected = etree.tostring(obj1)
        obj2 = objectify.fromstring(actual)
        actual = etree.tostring(obj2)

        # print(expected)
        # print("----------------")
        # print(actual)
        # print("")
        unittest.TestCase().assertEqual(expected, actual)
