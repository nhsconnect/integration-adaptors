import unittest

from integration_tests.xml.hl7_xml_assertor import Hl7XmlResponseAssertor


class AMQMessageAssertor(object):

    def __init__(self, message):
        self.message = message
        self.assertor = unittest.TestCase('__init__')

    def assert_property(self, property_name: str, expected_value: str):
        property_value = self.message.properties[property_name]
        self.assertor.assertEqual(property_value, expected_value, "Property of message does not equal expected value")

        return self

    def assertor_for_hl7_xml_message(self):
        return Hl7XmlResponseAssertor(self.message.body)