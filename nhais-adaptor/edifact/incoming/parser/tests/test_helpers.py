import unittest

from testfixtures import compare

import edifact.incoming.parser.helpers as helpers
from edifact.incoming.parser import EdifactDict


class TestParserHelpers(unittest.TestCase):

    def test_extract_relevant_lines(self):
        with self.subTest("When the original dict is just 1 line and terminating keys not found "
                          "return the original dict"):
            expected = EdifactDict([("AAA", "VALUE FOR AAA")])

            original_dict = EdifactDict([("AAA", "VALUE FOR AAA")])
            result = helpers.extract_relevant_lines(original_dict, starting_pos=0, terminator_keys=["BBB"])

            compare(result, expected)

        with self.subTest("When the terminating key is found on the first line"
                          "return an empty Edifact dict"):
            expected = EdifactDict([])

            original_dict = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB")])
            result = helpers.extract_relevant_lines(original_dict, starting_pos=0, terminator_keys=["AAA"])

            compare(result, expected)

        with self.subTest("When the original dict is multiple lines and terminating keys not found "
                          "return the original dict"):
            expected = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB")])

            original_dict = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB")])
            result = helpers.extract_relevant_lines(original_dict, starting_pos=0, terminator_keys=["CCC"])

            compare(result, expected)

        with self.subTest("When the starting pos is 0 and terminating key is found "
                          "return a new dict from the first line to the terminating key is found"):
            expected = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB")])

            original_dict = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB"), ("CCC", "VALUE FOR CCC")])
            result = helpers.extract_relevant_lines(original_dict, starting_pos=0, terminator_keys=["CCC"])

            compare(result, expected)

        with self.subTest("When the starting pos is 1 and terminating key is found "
                          "return a new dict from the second line to the terminating key is found"):
            expected = EdifactDict([("BBB", "VALUE FOR BBB")])

            original_dict = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB"), ("CCC", "VALUE FOR CCC")])
            result = helpers.extract_relevant_lines(original_dict, starting_pos=1, terminator_keys=["CCC"])

            compare(result, expected)

        with self.subTest("When the starting pos is 1 and terminating key is not found "
                          "return a new dict from the second line to the end of the original dict"):
            expected = EdifactDict([("BBB", "VALUE FOR BBB"), ("CCC", "VALUE FOR CCC")])

            original_dict = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB"), ("CCC", "VALUE FOR CCC")])
            result = helpers.extract_relevant_lines(original_dict, starting_pos=1, terminator_keys=["DDD"])

            compare(result, expected)

        with self.subTest("The terminator key exists on the first line but the starting pos is 1 "
                          "return a new dict from the second line to the terminating key is found"):
            expected = EdifactDict([("BBB", "VALUE FOR BBB")])

            original_dict = EdifactDict([("CCC", "VALUE FOR CCC"), ("BBB", "VALUE FOR BBB"), ("CCC", "VALUE FOR CCC")])
            result = helpers.extract_relevant_lines(original_dict, starting_pos=1, terminator_keys=["CCC"])

            compare(result, expected)

        with self.subTest("When more than one terminator key is provided "
                          "return a new dict from the starting pos to one of the terminating key is found"):
            expected = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB")])

            original_dict = EdifactDict([("AAA", "VALUE FOR AAA"), ("BBB", "VALUE FOR BBB"), ("CCC", "VALUE FOR CCC")])
            result = helpers.extract_relevant_lines(original_dict, starting_pos=0, terminator_keys=["CCC", "DDD"])

            compare(result, expected)

    def test_convert_to_dict(self):
        with self.subTest("Without duplicate keys"):
            expected = EdifactDict([
                ("AAA", "VALUE FOR AAA"),
                ("BBB", "VALUE FOR BBB"),
                ("CCC", "VALUE FOR CCC")
            ])

            input_lines = [
                "AAA+VALUE FOR AAA",
                "BBB+VALUE FOR BBB",
                "CCC+VALUE FOR CCC"
            ]
            converted_dict = helpers.convert_to_dict(input_lines)

            compare(converted_dict, expected)

        with self.subTest("With duplicate keys should still return duplicate keys in EdifactDict"):
            expected = EdifactDict([
                ("AAA", "VALUE FOR AAA"),
                ("BBB", "VALUE FOR BBB"),
                ("AAA", "VALUE FOR AAA")
            ])

            input_lines = [
                "AAA+VALUE FOR AAA",
                "BBB+VALUE FOR BBB",
                "AAA+VALUE FOR AAA"
            ]
            converted_dict = helpers.convert_to_dict(input_lines)

            compare(converted_dict, expected)
