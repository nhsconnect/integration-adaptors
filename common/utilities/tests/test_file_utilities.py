import os
from unittest import TestCase

from utilities.file_utilities import FileUtilities

TEST_FILE_DIR = "test_files"
TEST_FILE = "test.txt"
TEST_STRING = "Test String.\n"

CR_LF_STRING = "foo\r\nbar\r\nbaz"
CR_STRING = "foo\rbar\rbaz"
LF_STRING = "foo\nbar\nbaz"
MIXED_STRING = "foo\r\nbar\nbaz"
EXPECTED_NORMALIZED_STRING = "foo\nbar\nbaz"


class TestFileUtilities(TestCase):

    def test_get_file_string(self):
        current_dir = os.path.dirname(__file__)
        test_files_dir = os.path.join(current_dir, TEST_FILE_DIR)
        test_file = os.path.join(test_files_dir, TEST_FILE)

        loaded_string = FileUtilities.get_file_string(test_file)

        self.assertEqual(TEST_STRING, loaded_string, "The string loaded should match the one expected.")

    def test_normalize_line_endings(self):
        strings_to_test = {
            "CRLF": CR_LF_STRING,
            "CR": CR_STRING,
            "LF": LF_STRING,
            "Mixed": MIXED_STRING
        }

        for line_break_type in strings_to_test:
            message = line_break_type + " line endings should be normalized."

            with self.subTest(message):
                normalized_string = FileUtilities.normalize_line_endings(strings_to_test[line_break_type])

                self.assertEqual(EXPECTED_NORMALIZED_STRING, normalized_string)
