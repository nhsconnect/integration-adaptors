
from lxml import etree
from lxml import objectify
import unittest

class XmlHelper:

    @staticmethod
    def assertXmlStringsEqual(expected, actual):
        obj1 = objectify.fromstring(expected)
        expected = etree.tostring(obj1)
        obj2 = objectify.fromstring(actual)
        actual = etree.tostring(obj2)

        # print(expected)
        # print("----------------")
        # print(actual)
        # print("")
        unittest.TestCase().assertEqual(expected, actual)