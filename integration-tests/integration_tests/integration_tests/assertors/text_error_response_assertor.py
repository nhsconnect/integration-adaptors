"""
Provides assertions over the text response format we get from the MHS when an error is returned from Spine
"""
from __future__ import annotations
import re
import unittest


class TextErrorResponseAssertor(object):
    """
    Provides assertions over the text response format we get from the MHS when an error is returned from Spine
    """

    def __init__(self, received_message: str):
        """
        Create instance of class for making assertions over the received message
        :param received_message: the message to assert
        """
        self.received_message = received_message
        self.assertor = unittest.TestCase('__init__')

    def assert_error_code(self, expected_error_code: int) -> TextErrorResponseAssertor:
        """
        Assert the error code part of the message string
        :param expected_error_code: the error code expected
        :return: self
        """
        expression = re.compile('(errorCode=(?P<errorCode>[0-9]+))')
        matches = expression.search(self.received_message)
        if len(matches.groups()) != 2:
            raise Exception("No error code found in the returned string")

        matching_group = matches.group('errorCode')
        self.assertor.assertEqual(int(matching_group), expected_error_code, 'Error code did not match expected value')
        return self

    def assert_code_context(self, expected_code_context: str) -> TextErrorResponseAssertor:
        """
        Assert the code context part of the message string
        :param expected_code_context: the code context expected
        :return: self
        """
        expression = re.compile('(codeContext=(?P<codeContext>[a-zA-Z:]+))')
        matches = expression.search(self.received_message)
        if len(matches.groups()) != 2:
            raise Exception("No codeContext found in the returned string")

        matching_group = matches.group('codeContext')
        self.assertor.assertEqual(matching_group, expected_code_context, 'Code context did not match expected value')
        return self

    def assert_severity(self, expected_severity: str) -> TextErrorResponseAssertor:
        """
        Assert the severity part of the message string
        :param expected_severity: the severity expected
        :return: self
        """
        expression = re.compile('(severity=(?P<severity>[a-zA-Z]+))')
        matches = expression.search(self.received_message)
        if len(matches.groups()) != 2:
            raise Exception("No severity found in the returned string")

        matching_group = matches.group('severity')
        self.assertor.assertEqual(matching_group, expected_severity, 'Severity did not match expected value')
        return self
