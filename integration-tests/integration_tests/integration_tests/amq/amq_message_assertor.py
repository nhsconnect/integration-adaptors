"""
Provides a way of asserting AMQ messages
"""
from __future__ import annotations

import json
import unittest

from integration_tests.xml.hl7_xml_assertor import Hl7XmlResponseAssertor


class AMQMessageAssertor(object):
    """
    Provides the ability to assert properties of an AMQ message
    """

    def __init__(self, message):
        self.message = message
        self.assertor = unittest.TestCase('__init__')

    def assert_property(self, property_name: str, expected_value: str) -> AMQMessageAssertor:
        """
        Asserts a property of the AMQ message
        :param property_name: the property name to assert
        :param expected_value: the expected value
        :return: self
        """
        property_value = self.message.properties[property_name]
        self.assertor.assertEqual(property_value, expected_value, "Property of message does not equal expected value")

        return self

    def assert_json_content_type(self) -> AMQMessageAssertor:
        """Asserts the content type of the AMQ message is application/json"""
        self.assertor.assertEqual(self.message.content_type, 'application/json')

        return self


    def assertor_for_hl7_xml_message(self) -> Hl7XmlResponseAssertor:
        """
        Gets an assertor for the message body, when the message body is expected to be a HL7 XML message
        :return:
        """
        return Hl7XmlResponseAssertor(json.loads(self.message.body)['payload'])
