import unittest

from lxml import etree
from lxml import objectify
import xml
from xml import dom
from xml.dom.minidom import parseString


class XmlUtilities(object):

    @staticmethod
    def assert_xml_equal(expected, actual):
        """
        Given two strings of xml this method normalises them and asserts they are equal
        :param expected:
        :param actual:
        """
        obj1 = objectify.fromstring(expected)
        # expected = etree.tostring(obj1)
        obj2 = objectify.fromstring(actual)
        # actual = etree.tostring(obj2)

        # expected = parseString(expected).toprettyxml(indent='', newl='', encoding='UTF-8').decode('utf-8')
        # actual = parseString(actual).toprettyxml(indent='', newl='', encoding='UTF-8').decode('utf-8')

        parser = etree.XMLParser(remove_blank_text=True)
        # xml_str = '''<root>
        #     <head></head>
        #     <content></content>
        # </root>'''
        # elem = etree.XML(xml_str, parser=parser)
        # sss = etree.tostring(elem)

        s1 = etree.tostring(etree.XML(expected, parser=parser))
        s2 = etree.tostring(etree.XML(actual, parser=parser))

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
