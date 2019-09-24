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

    def assert_element_exists(self, xpath):
        self.__get_value(xpath)
        return self

    def assert_key_value(self, xpath: str, expected_value: Any) -> JsonResponseAssertor:
        value_at_xpath = self.__get_value(xpath)
        self.assertor.assertEqual(value_at_xpath, expected_value,
                                  f'Value at xpath does not equal expected value. '
                                  f'expected_value = {expected_value} value found={value_at_xpath}')

        return self

    def __get_value(self, xpath) -> Optional[Any]:
        try:
            value_at_xpath = dpath.util.get(self.json_response, xpath)
        except KeyError:
            value_at_xpath = None

        self.assertor.assertIsNotNone(value_at_xpath,
                                      f'Key with xpath: {xpath} not found in repsonse json: '
                                      f'{self.json_response}')
        return value_at_xpath
