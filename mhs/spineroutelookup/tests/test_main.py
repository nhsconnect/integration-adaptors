import unittest.mock

from utilities import config

import main
from lookup import dictionary_cache

CONFIG_PREFIX = "MHS"
CACHE_EXPIRY_TIME_KEY = "MHS_SDS_CACHE_EXPIRY_TIME"
DEFAULT_CACHE_EXPIRY_TIME = 900
CACHE_EXPIRY_TIME = 450


class TestMain(unittest.TestCase):
    @unittest.mock.patch("os.environ", new_callable=dict)
    @unittest.mock.patch.dict(config.config)
    def test_load_cache_implementation(self, mock_environment):
        mock_environment[CACHE_EXPIRY_TIME_KEY] = CACHE_EXPIRY_TIME
        config.setup_config(CONFIG_PREFIX)

        loaded_cache = main.load_cache_implementation()

        self.assertIsInstance(loaded_cache, dictionary_cache.DictionaryCache)
        self.assertEqual(loaded_cache.expiry_time, CACHE_EXPIRY_TIME)

    @unittest.mock.patch("os.environ", new_callable=dict)
    @unittest.mock.patch.dict(config.config)
    def test_load_cache_implementation_defaults(self, _):
        config.setup_config(CONFIG_PREFIX)

        loaded_cache = main.load_cache_implementation()

        self.assertIsInstance(loaded_cache, dictionary_cache.DictionaryCache)
        self.assertEqual(loaded_cache.expiry_time, DEFAULT_CACHE_EXPIRY_TIME)
