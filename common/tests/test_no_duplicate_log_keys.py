import os
import pathlib
import re
import unittest


class TestNoDuplicateLogKeys(unittest.TestCase):

    def setUp(self):
        self.current_folder = pathlib.Path(__file__).parent / '..'

    def test_no_duplicate_log_keys(self):
        logger_names = []

        for root, dirs, filenames in os.walk(str(self.current_folder)):
            if os.path.basename(root) == 'tests':
                continue
            for filename in filenames:
                if filename.endswith('.py') and not (filename.startswith('test_') or filename.startswith('int_')):
                    filepath = pathlib.Path(os.path.join(root, filename))
                    file_contents = filepath.read_text()

                    # Look for code matching IntegrationAdaptorsLogger("LOGGER_NAME")
                    logger_match = re.search(r'IntegrationAdaptorsLogger\([\'"](?P<loggerName>\w+)[\'"]', file_contents)
                    if not logger_match:
                        continue

                    with self.subTest(filename=filename, filepath=filepath):
                        logger_name = logger_match.group('loggerName')
                        logger_names.append(logger_name)

                        log_method_names_regex = r'info|audit|warning|error|critical'
                        log_keys_regex = rf'logger\.({log_method_names_regex})\([\'"](?P<logKey>\d+)[\'"]'
                        log_keys = [log_key for _, log_key in re.findall(log_keys_regex, file_contents)]

                        self.assertEqual(sorted(log_keys), sorted(set(log_keys)),
                                         msg=f'Duplicate log keys found in {filepath}')

        with self.subTest('Check no duplicate logger names'):
            self.assertEqual(sorted(logger_names), sorted(set(logger_names)), msg=f'Duplicate logger names found')
