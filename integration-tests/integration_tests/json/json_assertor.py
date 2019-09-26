"""
Provides methods for asserting the contents of a json message
"""
from __future__ import annotations
import json
from typing import Any, Optional
import dpath.util
import unittest


class JsonResponseAssertor(object):
    """An assertor that is able to valid the contents of a json response"""

    def __init__(self, json_response: str):
        self.json_response = json.loads(json_response)
        self.assertor = unittest.TestCase('__init__')

    def assert_key_exists(self, xpath):
        """
        Asserts there exists a key within the json at the given xpath
        :param xpath: The xpath of the key
        :return: self
        """
        self.__get_value(xpath)
        return self

    def assert_key_exists_with_value(self, xpath: str, expected_value: Any) -> JsonResponseAssertor:
        """
        Asserts whether the value at the given xpath is equal to a given expected valiue
        :param xpath:
        :param expected_value:
        :return: self
        """
        value_at_xpath = self.__get_value(xpath)
        self.assertor.assertEqual(value_at_xpath, expected_value,
                                  f'Value at xpath does not equal expected value. '
                                  f'expected_value = {expected_value} value found={value_at_xpath}')

        return self

    def __get_value(self, xpath) -> Optional[Any]:
        """
        Attempts to get the value associated with the key at the given xpath, with raise KeyError if no key at the xpath
        exists, and asserts the value at that xpath is not None
        :param xpath: The xpath of the desired key/value
        :return: The value at the given xpath
        """
        values = dpath.util.search(self.json_response, xpath)

        self.assertor.assertEqual(len(values.keys()), 1,
                                  f'Failed to find exactly one key with the given xpath, found: {values}')
        return dpath.util.get(self.json_response, xpath)
