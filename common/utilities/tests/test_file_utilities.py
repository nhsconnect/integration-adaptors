import os
from unittest import TestCase

import utilities.file_utilities as file_utilities

TEST_FILE_DIR = "test_files"

TEST_FILE = "test.txt"
EXPECTED_STRING = "Test String.\n"

TEST_JSON_FILE = "test.json"
EXPECTED_JSON = {"one": "foo", "two": "bar"}

CR_LF_STRING = "foo\r\nbar\r\nbaz"
CR_STRING = "foo\rbar\rbaz"
LF_STRING = "foo\nbar\nbaz"
MIXED_STRING = "foo\r\nbar\nbaz"
EXPECTED_NORMALIZED_STRING = "foo\nbar\nbaz"


class TestFileUtilities(TestCase):
    current_dir = os.path.dirname(__file__)
    test_files_dir = os.path.join(current_dir, TEST_FILE_DIR)

    def test_get_file_string(self):
        test_file = os.path.join(self.test_files_dir, TEST_FILE)

        loaded_string = file_utilities.get_file_string(test_file)

        self.assertEqual(EXPECTED_STRING, loaded_string, "The string loaded should match the one expected.")

    def test_get_file_dict(self):
        test_json_file = os.path.join(self.test_files_dir, TEST_JSON_FILE)

        loaded_dict = file_utilities.get_file_dict(test_json_file)

        self.assertEqual(EXPECTED_JSON, loaded_dict, "The dictionary loaded should match the one expected.")

    def test_normalize_line_endings(self):
        strings_to_test = {
            "CRLF": CR_LF_STRING,
            "CR": CR_STRING,
            "LF": LF_STRING,
            "Mixed": MIXED_STRING
        }

        for line_break_type, test_string in strings_to_test.items():
            message = line_break_type + " line endings should be normalized."

            with self.subTest(message):
                normalized_string = file_utilities.normalize_line_endings(test_string)

                self.assertEqual(EXPECTED_NORMALIZED_STRING, normalized_string)
