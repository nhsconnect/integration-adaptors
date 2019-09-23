import unittest.mock

from utilities import config

import main
from lookup import redis_cache

CONFIG_PREFIX = "MHS"
CACHE_EXPIRY_TIME_KEY = "MHS_SDS_CACHE_EXPIRY_TIME"
DEFAULT_CACHE_EXPIRY_TIME = 900
CACHE_EXPIRY_TIME = 450
CACHE_HOST_KEY = "MHS_SDS_REDIS_CACHE_HOST"
CACHE_HOST = "localhost"
CACHE_PORT_KEY = "MHS_SDS_REDIS_CACHE_PORT"
CACHE_PORT = "6379"
CACHE_DISABLE_TLS_KEY = "MHS_SDS_REDIS_CACHE_PORT"
DISABLE_TLS = "True"


class TestMain(unittest.TestCase):
    @unittest.mock.patch("os.environ", new_callable=dict)
    @unittest.mock.patch.dict(config.config)
    def test_load_cache_implementation(self, mock_environment):
        mock_environment[CACHE_EXPIRY_TIME_KEY] = CACHE_EXPIRY_TIME
        mock_environment[CACHE_HOST_KEY] = CACHE_HOST
        mock_environment[CACHE_PORT_KEY] = CACHE_PORT
        mock_environment[DISABLE_TLS] = DISABLE_TLS
        config.setup_config(CONFIG_PREFIX)

        loaded_cache = main.load_cache_implementation()

        self.assertIsInstance(loaded_cache, redis_cache.RedisCache)
        self.assertEqual(loaded_cache.expiry_time, CACHE_EXPIRY_TIME)

    @unittest.mock.patch("os.environ", new_callable=dict)
    @unittest.mock.patch.dict(config.config)
    def test_load_cache_implementation_defaults(self, mock_environment):
        mock_environment[CACHE_HOST_KEY] = CACHE_HOST
        config.setup_config(CONFIG_PREFIX)

        loaded_cache = main.load_cache_implementation()

        self.assertIsInstance(loaded_cache, redis_cache.RedisCache)
        self.assertEqual(loaded_cache.expiry_time, DEFAULT_CACHE_EXPIRY_TIME)
