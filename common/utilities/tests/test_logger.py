import io
import logging
from unittest import TestCase
from unittest.mock import patch, MagicMock
from common.utilities import integration_adapters_logger as log


class TestLogger(TestCase):

    def test_dictionary_formatting(self):
        # Tests both removing the spaces and surrounding values with quotes if needed
        input_dict = {
            'Key With Space': 'value with space',  # Needs quotes
            'EasyKey': 'EasyValue',  # Doesn't need quotes
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
        log.IntegrationAdaptersLogger('TES') \
            .info('{There Will Be No Spaces Today}', {'There Will Be No Spaces Today': 'wow qwe'}, correlation_id=2)

        output = mock_std.getvalue()
        self.assertIn('CorrelationId=2', output)
        self.assertIn('ThereWillBeNoSpacesToday="wow qwe"', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_format_and_write(self, mock_std):
        log.load_global_log_config()
        log.IntegrationAdaptersLogger()._format_and_write(
            message="{yes} {no} {maybe}",
            values={'yes': 'one', 'no': 'two', 'maybe': 'three'},
            request_id=10,
            correlation_id=5,
            level=logging.INFO,
            process_key_num="100"
        )

        output = mock_std.getvalue()

        # Check that each value has spaces
        self.assertIn(' CorrelationId=5 ', output)
        self.assertIn(' LogLevel=INFO ', output)
        self.assertIn(' ProcessKey=SYS100', output)
        self.assertIn(' RequestId=10 ', output)
        self.assertIn(' maybe=three ', output)
        self.assertIn(' yes=one ', output)
        self.assertIn(' pid=', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_format_and_write_empty_vals(self, mock_std):
        log.load_global_log_config()
        log.IntegrationAdaptersLogger()._format_and_write(
            message="{yes} {no} {maybe}",
            values={'yes': 'one', 'no': 'two', 'maybe': 'three'},
            request_id=None,
            correlation_id=None,
            level=logging.INFO,
            process_key_num="100"
        )

        output = mock_std.getvalue()
        self.assertIn(' LogLevel=INFO ', output)
        self.assertIn(' ProcessKey=SYS100', output)
        self.assertIn(' maybe=three ', output)
        self.assertIn(' pid=', output)
        self.assertIn(' yes=one ', output)

    def test_log_levels(self):
        logger = log.IntegrationAdaptersLogger()
        logger._format_and_write = MagicMock()
        with self.subTest("INFO"):
            logger.info("{yes}", {'yes': 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes': 'no'}, "100", "REQ", 313, logging.INFO)

        with self.subTest("AUDIT"):
            logger.audit("{yes}", {'yes': 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes': 'no'}, "100", "REQ", 313, log.AUDIT)

        with self.subTest("WARNING"):
            logger.warning("{yes}", {'yes': 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes': 'no'}, "100", "REQ", 313, logging.WARNING)

        with self.subTest("ERROR"):
            logger.error("{yes}", {'yes': 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes': 'no'}, "100", "REQ", 313, logging.ERROR)

        with self.subTest("CRITICAL"):
            logger.critical("{yes}", {'yes': 'no'}, "100", "REQ", 313)
            logger._format_and_write.assert_called_with("{yes}", {'yes': 'no'}, "100", "REQ", 313, logging.CRITICAL)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_empty_values(self, mock_stdout):
        log.load_global_log_config()
        logger = log.IntegrationAdaptersLogger()
        with self.subTest("Empty info log"):
            logger.info("I can still log info strings without values!")
            output = mock_stdout.getvalue()
            self.assertIn('I can still log info strings without values!', output)
        with self.subTest("Empty audit log"):
            logger.audit("I can still log audit strings without values!")
            output = mock_stdout.getvalue()
            self.assertIn('I can still log audit strings without values!', output)
        with self.subTest("Empty warning log"):
            logger.warning("I can still log warning strings without values!")
            output = mock_stdout.getvalue()
            self.assertIn('I can still log warning strings without values!', output)
        with self.subTest("Empty error log"):
            logger.error("I can still log error strings without values!")
            output = mock_stdout.getvalue()
            self.assertIn('I can still log error strings without values!', output)
        with self.subTest("Empty Critical log"):
            logger.critical("I can still log critical strings without values!")
            output = mock_stdout.getvalue()
            self.assertIn('I can still log critical strings without values!', output)


