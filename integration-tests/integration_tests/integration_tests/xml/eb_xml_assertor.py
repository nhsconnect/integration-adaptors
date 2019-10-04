"""
Provides a way of asserting a EBXML message
"""
from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from typing import Any


class EbXmlResponseAssertor(object):
    """
    Assertor that is able to validate parts of an EBXML response
    """

    def __init__(self, xml: str):
        """
        The EB xml message is passed as a string, then converted to an element tree
        :param xml: the EBXML message
        """
        self.root_xml = ET.fromstring(xml)
        self.assertor = unittest.TestCase('__init__')

    def assert_element_exists(self, xpath: str) -> EbXmlResponseAssertor:
        """
        Asserts that the element with the given xpath exists within the xml.
        :param xpath: the xpath to search for
        :return: self
        """
        self.__get_element(xpath)
        return self

    def assert_element_exists_with_value(self, xpath: str, expected_value: str):
        """
        Asserts an element exists and contains the expected value
        :param xpath: the xpath of the element
        :param expected_value: the expected value of the element
        :return: self
        """
        element = self.__get_element(xpath)
        actual_value = element.text
        self.assertor.assertEqual(actual_value, expected_value,
                                  f"Expected value: {expected_value} not equal to actual value: {actual_value}")
        return self

    def assert_element_attribute(self, xpath: str, attribute: str, expected_value: Any) -> EbXmlResponseAssertor:
        """
        Asserts an element exists and has an attribute with the expected value
        :param xpath: the xpath of the element
        :param attribute: the attribute on the element to assert
        :param expected_value: the expected value of the attribute
        :return: self
        """
        element = self.__get_element(xpath)
        eb_attribute_key = f"{{http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd}}{attribute}"
        attribute_value = element.attrib[eb_attribute_key]
        self.assertor.assertEqual(attribute_value, expected_value,
                                  f"Expected attribute: {expected_value} not equal to actual value: {attribute_value}")
        return self

    def __get_element(self, xpath: str) -> ET.Element:
        """
        Gets an element within the XML, converting a normal XPath expression to use a EBXML namespace
        :param xpath: the xpath of the element
        :return: the matching element
        """
        eb_xpath = re.sub(r"[/]{2}", "//eb:", xpath)
        element_matching_xpath = self.root_xml.find(eb_xpath, namespaces={'eb': 'http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd'})
        self.assertor.assertIsNotNone(element_matching_xpath,
                                      f"element with xpath: {eb_xpath} not found in: {self.root_xml}")
        return element_matching_xpath
