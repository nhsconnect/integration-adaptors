import unittest

from utilities.string_utilities import str2bool


class TestStringUtilities(unittest.TestCase):

    def test_values_are_correctly_parsed_to_True(self):
        for value in ['true', 'True', 'TRUE']:
            self.assertTrue(str2bool(value))

    def test_values_are_correctly_parsed_to_False(self):
        for value in ['false', 'False', 'FALSE']:
            self.assertFalse(str2bool(value))

    def test_incorrect_values_raise_exception(self):
        for value in ['', ' ', '123', 'qwe', 'true1']:
            self.assertRaises(ValueError, str2bool, value)
