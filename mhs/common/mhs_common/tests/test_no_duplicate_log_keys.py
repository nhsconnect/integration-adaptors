import pathlib

import tests.test_no_duplicate_log_keys


class TestNoDuplicateLogKeys(tests.test_no_duplicate_log_keys.TestNoDuplicateLogKeys):

    def setUp(self):
        self.current_folder = pathlib.Path(__file__).parent / '..'
