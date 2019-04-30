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
        normalized_crlf_string = FileUtilities.normalize_line_endings(CR_LF_STRING)
        normalized_cr_string = FileUtilities.normalize_line_endings(CR_STRING)
        normalized_lf_string = FileUtilities.normalize_line_endings(LF_STRING)
        normalized_mixed_string = FileUtilities.normalize_line_endings(MIXED_STRING)

        self.assertEqual(EXPECTED_NORMALIZED_STRING, normalized_crlf_string, "CRLF line endings should be normalized.")
        self.assertEqual(EXPECTED_NORMALIZED_STRING, normalized_cr_string, "LF line endings should be normalized.")
        self.assertEqual(EXPECTED_NORMALIZED_STRING, normalized_lf_string, "LF line endings should be normalized.")
        self.assertEqual(EXPECTED_NORMALIZED_STRING, normalized_mixed_string,
                         "Mixed line endings should be normalized.")
