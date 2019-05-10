import unittest

from testfixtures import compare
from edifact.incoming.parser import EdifactDict
import edifact.incoming.parser.deserialiser as deserialiser


class TestConvertToDict(unittest.TestCase):
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
            converted_dict = deserialiser.convert_to_dict(input_lines)

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
            converted_dict = deserialiser.convert_to_dict(input_lines)

            compare(converted_dict, expected)