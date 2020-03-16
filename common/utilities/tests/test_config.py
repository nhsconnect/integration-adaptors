import io
import logging
import unittest
from unittest.mock import patch

import utilities.config as config
from utilities import integration_adaptors_logger
from utilities.tests.test_logger import LogEntry


@patch.dict(config.config)
@patch("os.environ", new_callable=dict)
class TestConfig(unittest.TestCase):

    def test_setup_config_populates_config(self, mock_environ):
        mock_environ["PREFIX_TEST"] = "123"
        mock_environ["PREFIX_LOG_LEVEL"] = "INFO"

        self.assertEqual({}, config.config)

        config.setup_config("PREFIX")

        self.assertEqual({"TEST": "123", "LOG_LEVEL": "INFO"}, config.config)

    def test_setup_config_filters_by_prefix(self, mock_environ):
        mock_environ["SOME_OTHER_CONFIG"] = "BLAH"

        config.setup_config("PREFIX")

        self.assertEqual({}, config.config)

    def test_get_config_success(self, mock_environ):
        mock_environ["PREFIX_TEST"] = "123"

        config.setup_config("PREFIX")

        self.assertEqual("123", config.get_config("TEST"))

    def test_get_config_default(self, mock_environ):
        mock_environ["PREFIX_TEST"] = "123"

        config.setup_config("PREFIX")

        self.assertEqual("111", config.get_config("LOG_LEVEL", default="111"))

    def test_get_config_default_none(self, unused):
        self.assertIsNone(config.get_config("LOG_LEVEL", default=None))

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_get_config_no_config_variable_found(self, mock_stdout, mock_environ):
        mock_environ["PREFIX_LOG_LEVEL"] = "INFO"
        config.setup_config("PREFIX")

        def remove_logging_handler():
            logging.getLogger().handlers = []

        self.addCleanup(remove_logging_handler)
        integration_adaptors_logger.configure_logging()

        with self.assertRaises(KeyError):
            config.get_config("BLAH")

        output = mock_stdout.getvalue()
        log_entry = LogEntry(output)
        self.assertEqual('Failed to get config ConfigName="BLAH"', log_entry.message)
        self.assertEqual('ERROR', log_entry.level)
