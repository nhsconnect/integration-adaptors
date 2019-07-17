import io
import logging
from unittest import TestCase
from unittest.mock import patch, MagicMock
import re

from common.utilities import logger as log

# This is the regex use to extract the key=value formatted log strings into dictionaries for testing
KEY_PAIR_REGEX = r'(\S+)=(".*?"|\S+)'


class TestLogger(TestCase):

    def test_dictionary_formatting(self):
        # Tests both removing the spaces and surrounding values with quotes if needed
        input_dict = {
            'Key With Space': 'value with space',
            'EasyKey': 'EasyValue'
        }

        expected_output = {
            'Key With Space': 'KeyWithSpace="value with space"',
            'EasyKey': 'EasyKey=EasyValue'
        }
        output = log._format_values_in_map(input_dict)
        self.assertEqual(output, expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_audit(self, mock_std):
        log.load_global_log_config()
        log.Logger('TES') \
            .info('{There Will Be No Spaces Today}', {'There Will Be No Spaces Today': 'wow qwe'}, correlation_id=2)

        output = mock_std.getvalue()
        output_dict = dict(re.findall(KEY_PAIR_REGEX, output))
        self.assertEqual(output_dict['CorrelationId'], "2")
        self.assertEqual(output_dict["ThereWillBeNoSpacesToday"], '"wow qwe"')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_format_and_write(self, mock_std):
        log.load_global_log_config()
        log.Logger()._format_and_write(
            message="{yes} {no} {maybe}",
            values={'yes': 'one', 'no': 'two', 'maybe': 'three'},
            request_id=10,
            correlation_id=5,
            level=logging.INFO,
            process_key_num="100"
        )

        output = mock_std.getvalue()
        output_dict = dict(re.findall(KEY_PAIR_REGEX, output))
        self.assertEqual(output_dict['CorrelationId'], '5')
        self.assertEqual(output_dict['LogLevel'], 'INFO')
        self.assertEqual(output_dict['ProcessKey'], 'SYS100')
        self.assertEqual(output_dict['RequestId'], '10')
        self.assertEqual(output_dict['maybe'], 'three')
        self.assertIsNotNone(output_dict['pid'])
        self.assertEqual(output_dict['yes'], 'one')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_format_and_write_empty_vals(self, mock_std):
        log.load_global_log_config()
        log.Logger()._format_and_write(
            message="{yes} {no} {maybe}",
            values={'yes': 'one', 'no': 'two', 'maybe': 'three'},
            request_id=None,
            correlation_id=None,
            level=logging.INFO,
            process_key_num="100"
        )

        output = mock_std.getvalue()
        output_dict = dict(re.findall(r'(\S+)=(".*?"|\S+)', output))
        self.assertEqual(output_dict['LogLevel'], 'INFO')
        self.assertEqual(output_dict['ProcessKey'], 'SYS100')
        self.assertEqual(output_dict['maybe'], 'three')
        self.assertIsNotNone(output_dict['pid'])
        self.assertEqual(output_dict['yes'], 'one')

    def test_log_levels(self):
        logger = log.Logger()
        logger._format_and_write = MagicMock()
        with self.subTest("INFO"):
            logger.info("{yes}", {'yes', 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes', 'no'}, "100", "REQ", 313, logging.INFO)

        with self.subTest("AUDIT"):
            logger.audit("{yes}", {'yes', 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes', 'no'}, "100", "REQ", 313, log.AUDIT)

        with self.subTest("WARNING"):
            logger.warning("{yes}", {'yes', 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes', 'no'}, "100", "REQ", 313, logging.WARNING)

        with self.subTest("ERROR"):
            logger.error("{yes}", {'yes', 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes', 'no'}, "100", "REQ", 313, logging.ERROR)

        with self.subTest("CRITICAL"):
            logger.critical("{yes}", {'yes', 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes', 'no'}, "100", "REQ", 313, logging.CRITICAL)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_crit_writes_to_stdout(self, mock_stdout):
        log.load_global_log_config()
        log.Logger('FAR') \
            .critical(message='This is a {key}',
                      values={'key': 'great value'},
                      process_key_num="541",
                      request_id="313",
                      correlation_id=2)

        output = mock_stdout.getvalue()
        text = output.split(']')[1]  # Get rid of the time section
        # Asserts non key value text is written as well
        self.assertTrue('This is a key="great value"' in text)

        self.assertTrue('CorrelationId=2' in text)
        self.assertTrue('key="great value"' in text)
        self.assertTrue('RequestId=313' in text)
        self.assertTrue('LogLevel=CRITICAL' in text)

