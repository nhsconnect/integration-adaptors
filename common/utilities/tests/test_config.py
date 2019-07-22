import unittest
from unittest.mock import patch

import utilities.config as config


@patch("utilities.config.config", new_callable=dict)
@patch("os.environ", new_callable=dict)
class TestConfig(unittest.TestCase):

    def test_setup_config_populates_config(self, mock_environ, _unused):
        mock_environ["PREFIX_TEST"] = "123"
        mock_environ["PREFIX_LOG_LEVEL"] = "INFO"

        self.assertEqual({}, config.config)

        config.setup_config("PREFIX")

        self.assertEqual({"TEST": "123", "LOG_LEVEL": "INFO"}, config.config)

    def test_setup_config_filters_by_prefix(self, mock_environ, _unused):
        mock_environ["SOME_OTHER_CONFIG"] = "BLAH"

        config.setup_config("PREFIX")

        self.assertEqual({}, config.config)
