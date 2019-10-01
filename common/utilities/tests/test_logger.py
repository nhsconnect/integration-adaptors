import io
import logging
import os
import time
from unittest import TestCase
from unittest.mock import patch, MagicMock

from utilities import integration_adaptors_logger as log, config


@patch("utilities.config.config", new={'LOG_LEVEL': 'INFO'})
class TestLogger(TestCase):

    def tearDown(self) -> None:
        logging.getLogger().handlers = []
        log.message_id.set(None)
        log.correlation_id.set(None)
        log.interaction_id.set(None)

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
        output = log.IntegrationAdaptorsLogger('SYS')._format_values_in_map(input_dict)
        self.assertEqual(output, expected_output)

    def test_dictionary_with_non_string_values(self):
        input_dict = {
            'EasyKey': False
        }

        expected_output = {
            'EasyKey': 'EasyKey=False'
        }
        output = log.IntegrationAdaptorsLogger('SYS')._format_values_in_map(input_dict)
        self.assertEqual(output, expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_interaction_id_context_var_should_be_logged_when_set(self, mock_stdout):
        # Arrange
        log.configure_logging()
        log.interaction_id.set('GP_101')
        logger = log.IntegrationAdaptorsLogger('TES')

        # Act
        logger.audit('100', 'This log message should have interaction id ')
        output = mock_stdout.getvalue()

        # Assert
        self.assertIn('InteractionId=GP_101', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_custom_audit_level(self, mock_stdout):
        log.configure_logging()
        log.correlation_id.set('2')
        log.IntegrationAdaptorsLogger('TES') \
            .audit('100', '{There Will Be No Spaces Today}',
                   {'There Will Be No Spaces Today': 'wow qwe'})

        output = mock_stdout.getvalue()
        self.assertIn('CorrelationId=2', output)
        self.assertIn('ThereWillBeNoSpacesToday="wow qwe"', output)
        self.assertIn('LogLevel=AUDIT', output)
        self.assertIn('ProcessKey=TES100', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_log_threshold(self, mock_stdout):
        config.config['LOG_LEVEL'] = 'AUDIT'
        log.configure_logging()
        log.IntegrationAdaptorsLogger('TES').info('100', 'Test message')

        output = mock_stdout.getvalue()
        self.assertEqual("", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_format_and_write(self, mock_std):
        log.configure_logging()
        log.message_id.set('10')
        log.correlation_id.set('5')
        log.inbound_message_id.set('8')

        log.IntegrationAdaptorsLogger('SYS')._format_and_write(
            message='{yes} {no} {maybe}',
            values={'yes': 'one', 'no': 'two', 'maybe': 'three'},
            level=logging.INFO,
            process_key_num='100'
        )

        output = mock_std.getvalue()

        # Check that each value has spaces
        self.assertIn(' CorrelationId=5 ', output)
        self.assertIn(' LogLevel=INFO ', output)
        self.assertIn(' ProcessKey=SYS100', output)
        self.assertIn(' RequestId=10 ', output)
        self.assertIn(' maybe=three ', output)
        self.assertIn(' yes=one ', output)
        self.assertIn(f' pid={os.getpid()}', output)
        self.assertIn('InboundMessageId=8', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_format_and_write_empty_vals(self, mock_std):
        log.configure_logging()
        log.IntegrationAdaptorsLogger('SYS')._format_and_write(
            message='{yes} {no} {maybe}',
            values={'yes': 'one', 'no': 'two', 'maybe': 'three'},
            level=logging.INFO,
            process_key_num='100'
        )

        output = mock_std.getvalue()
        self.assertIn(' LogLevel=INFO ', output)
        self.assertIn(' ProcessKey=SYS100', output)
        self.assertIn(' maybe=three ', output)
        self.assertIn(f' pid={os.getpid()}', output)
        self.assertIn(' yes=one ', output)
        self.assertNotIn('CorrelationId=', output)
        self.assertNotIn('RequestId=', output)

    def test_log_levels(self):
        logger = log.IntegrationAdaptorsLogger('SYS')
        logger._format_and_write = MagicMock()
        with self.subTest('INFO'):
            logger.info('100', '{yes}', {'yes': 'no'})
            logger._format_and_write.assert_called_with('{yes}', {'yes': 'no'}, '100', logging.INFO)

        with self.subTest('AUDIT'):
            logger.audit('100', '{yes}', {'yes': 'no'})
            logger._format_and_write.assert_called_with('{yes}', {'yes': 'no'}, '100', log.AUDIT)

        with self.subTest('WARNING'):
            logger.warning('100', '{yes}', {'yes': 'no'})
            logger._format_and_write.assert_called_with('{yes}', {'yes': 'no'}, '100', logging.WARNING)

        with self.subTest('ERROR'):
            logger.error('100', '{yes}', {'yes': 'no'})
            logger._format_and_write.assert_called_with('{yes}', {'yes': 'no'}, '100', logging.ERROR)

        with self.subTest('CRITICAL'):
            logger.critical('100', '{yes}', {'yes': 'no'})
            logger._format_and_write.assert_called_with('{yes}', {'yes': 'no'}, '100', logging.CRITICAL)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_empty_values(self, mock_stdout):
        log.configure_logging()
        logger = log.IntegrationAdaptorsLogger('SYS')
        with self.subTest('Empty info log'):
            logger.info('100', 'I can still log info strings without values!')
            output = mock_stdout.getvalue()
            self.assertIn('I can still log info strings without values!', output)
        with self.subTest('Empty audit log'):
            logger.audit('100', 'I can still log audit strings without values!')
            output = mock_stdout.getvalue()
            self.assertIn('I can still log audit strings without values!', output)
        with self.subTest('Empty warning log'):
            logger.warning('100', 'I can still log warning strings without values!')
            output = mock_stdout.getvalue()
            self.assertIn('I can still log warning strings without values!', output)
        with self.subTest('Empty error log'):
            logger.error('100', 'I can still log error strings without values!')
            output = mock_stdout.getvalue()
            self.assertIn('I can still log error strings without values!', output)
        with self.subTest('Empty Critical log'):
            logger.critical('100', 'I can still log critical strings without values!')
            output = mock_stdout.getvalue()
            self.assertIn('I can still log critical strings without values!', output)

    def test_write_throws_error_on_bad_params(self):
        with self.assertRaises(ValueError):
            log.IntegrationAdaptorsLogger('SYS')._format_and_write("message", {}, "", logging.INFO)

        with self.assertRaises(ValueError):
            log.IntegrationAdaptorsLogger('SYS')._format_and_write("message", {}, None, logging.INFO)

    def test_undefined_log_ref_throws_error(self):
        with self.assertRaises(ValueError):
            log.IntegrationAdaptorsLogger('')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_correct_time_format(self, mock_stdout):
        log.configure_logging()
        logger = log.IntegrationAdaptorsLogger('SYS')
        logger.info('100', 'I can still log info strings without values!')
        output = mock_stdout.getvalue()

        time_value = output.split('[')[1].split(']')[0]
        time.strptime(time_value, '%Y-%m-%dT%H:%M:%S.%fZ')

    @patch('utilities.config.get_config')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_should_log_critical_message_if_log_level_is_below_info(self, mock_stdout, mock_config):
        unsafe_log_levels = ['NOTSET', 'DEBUG']
        for level in unsafe_log_levels:
            with self.subTest(f'Log level {level} should result in critical log message being logged out'):
                mock_config.return_value = level
                log.configure_logging()
                output = mock_stdout.getvalue()
                self.assertIn(f'The current log level (logLevel={level}) is set below INFO level,'
                              f' it is known that libraries used '
                              'by this application sometimes log out clinical patient data at DEBUG level. '
                              'The log level provided MUST NOT be used in a production environment.', output)

    @patch('utilities.config.get_config')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_should_not_log_critical_message_if_log_level_is_above_debug(self, mock_stdout, mock_config):
        safe_log_levels = ['INFO', 'AUDIT', 'WARNING', 'ERROR', 'CRITICAL']
        for level in safe_log_levels:
            with self.subTest(f'Log level {level} should not result in critical log message being logged out'):
                mock_config.return_value = level
                log.configure_logging()
                output = mock_stdout.getvalue()
                self.assertEqual('', output)
