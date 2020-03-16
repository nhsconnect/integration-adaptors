import io
import logging
import unittest
from unittest.mock import patch

import utilities.config as config
from utilities import integration_adaptors_logger, secrets
from utilities.tests.test_logger import LogEntry


@patch.dict(secrets.secret_config)
@patch("os.environ", new_callable=dict)
class TestSecrets(unittest.TestCase):

    def test_setup_secret_config_populates_secret_config(self, mock_environ):
        mock_environ["PREFIX_SECRET_TEST"] = "123"
        mock_environ["PREFIX_SECRET_LOG_LEVEL"] = "INFO"

        self.assertEqual({}, secrets.secret_config)

        secrets.setup_secret_config("PREFIX")

        self.assertEqual({"TEST": "123", "LOG_LEVEL": "INFO"}, secrets.secret_config)

    def test_setup_secret_config_filters_by_prefix(self, mock_environ):
        mock_environ["SOME_OTHER_SECRET_CONFIG"] = "BLAH"

        secrets.setup_secret_config("PREFIX")

        self.assertEqual({}, secrets.secret_config)

    @patch.dict(config.config)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_get_secret_config_success(self, mock_stdout, mock_environ):
        self.setup_logger(mock_environ)

        secret_value = "123547"
        mock_environ["PREFIX_SECRET_TEST"] = secret_value

        secrets.setup_secret_config("PREFIX")

        self.assertEqual(secret_value, secrets.get_secret_config("TEST"))

        output = mock_stdout.getvalue()
        self.assertIn('Obtained secret config', output)
        self.assertNotIn(secret_value, output, msg="Secret value logged when it shouldn't be logged")

    def test_get_secret_config_default(self, mock_environ):
        mock_environ["PREFIX_SECRET_TEST"] = "123"

        secrets.setup_secret_config("PREFIX")

        self.assertEqual("111", secrets.get_secret_config("LOG_LEVEL", default="111"))

    def test_get_secret_config_default_none(self, unused):
        self.assertIsNone(secrets.get_secret_config("LOG_LEVEL", default=None))

    @patch.dict(config.config)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_get_secret_config_no_config_variable_found(self, mock_stdout, mock_environ):
        self.setup_logger(mock_environ)

        with self.assertRaises(KeyError):
            secrets.get_secret_config("BLAH")

        output = mock_stdout.getvalue()
        log_entry = LogEntry(output)
        self.assertEqual('Failed to get secret config ConfigName="BLAH"', log_entry.message)
        self.assertEqual("ERROR", log_entry.level)

    def setup_logger(self, mock_environ):
        mock_environ["PREFIX_LOG_LEVEL"] = "INFO"
        config.setup_config("PREFIX")

        def remove_logging_handler():
            logging.getLogger().handlers = []

        self.addCleanup(remove_logging_handler)
        integration_adaptors_logger.configure_logging()
