import json
import unittest.mock

import redis
from utilities.test_utilities import async_test

from lookup import redis_cache

REDIS_HOST = "host"
REDIS_PORT = 1234
USE_TLS = False

ODS_CODE = "ods"
INTERACTION_ID = "interaction-id"

VALUE_DICTIONARY = {
    "key1": "value1",
    "key2": ["list_entry_1", "list_entry_2"],
    "key3": {
        "nested_key_1": "nested_value_1",
        "nested_key_2": "nested_value_2"
    }
}

FIFTEEN_MINUTES_IN_SECONDS = 900


class TestRedisCache(unittest.TestCase):

    def setUp(self) -> None:
        # Mock the redis.Redis() constructor
        patcher = unittest.mock.patch.object(redis, "Redis")
        self.mock_redis_constructor = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the Redis client class itself
        self.mock_redis = unittest.mock.MagicMock()
        self.mock_redis_constructor.return_value = self.mock_redis

        self.cache = redis_cache.RedisCache(REDIS_HOST, REDIS_PORT, use_tls=USE_TLS)

    def test_redis_params_are_passed(self):
        self.mock_redis_constructor.assert_called_with(host=REDIS_HOST, port=REDIS_PORT, ssl=USE_TLS)

    def test_tls_is_enabled_by_default(self):
        redis_cache.RedisCache(REDIS_HOST, REDIS_PORT)

        self.mock_redis_constructor.assert_called_with(host=REDIS_HOST, port=REDIS_PORT, ssl=True)

    @async_test
    async def test_get_value(self):
        self.mock_redis.get.return_value = json.dumps(VALUE_DICTIONARY).encode()

        value = await self.cache.retrieve_mhs_attributes_value(ODS_CODE, INTERACTION_ID)

        self.assertEqual(value, VALUE_DICTIONARY)
        self.mock_redis.get.assert_called_with(self._generate_key())

    @async_test
    async def test_get_empty_value(self):
        self.mock_redis.get.return_value = None

        value = await self.cache.retrieve_mhs_attributes_value(ODS_CODE, INTERACTION_ID)

        self.assertIsNone(value)

    @async_test
    async def test_get_non_json_value(self):
        self.mock_redis.get.return_value = b"Not JSON"

        value = await self.cache.retrieve_mhs_attributes_value(ODS_CODE, INTERACTION_ID)

        self.assertIsNone(value)

    @async_test
    async def test_get_handles_redis_error(self):
        self.mock_redis.get.side_effect = redis.RedisError

        value = await self.cache.retrieve_mhs_attributes_value(ODS_CODE, INTERACTION_ID)

        self.assertIsNone(value)

    @async_test
    async def test_add_cache_entry(self):
        await self.cache.add_cache_value(ODS_CODE, INTERACTION_ID, VALUE_DICTIONARY)

        self.mock_redis.setex.assert_called_with(self._generate_key(), FIFTEEN_MINUTES_IN_SECONDS,
                                                 json.dumps(VALUE_DICTIONARY))

    @async_test
    async def test_add_cache_entry_overrides_default_timeout(self):
        custom_expiry_time = 27
        cache = redis_cache.RedisCache(REDIS_HOST, REDIS_PORT, expiry_time=custom_expiry_time)

        await cache.add_cache_value(ODS_CODE, INTERACTION_ID, VALUE_DICTIONARY)

        self.mock_redis.setex.assert_called_with(self._generate_key(), custom_expiry_time,
                                                 json.dumps(VALUE_DICTIONARY))

    @unittest.mock.patch.object(redis_cache, "logger")
    @async_test
    async def test_add_cache_entry_handles_redis_error(self, log_mock):
        error_raised = redis.RedisError()
        self.mock_redis.setex.side_effect = error_raised

        await self.cache.add_cache_value(ODS_CODE, INTERACTION_ID, VALUE_DICTIONARY)

        log_mock.warning.assert_called_with("0008", "An error occurred when caching {value}. {exception}",
                                            {"value": json.dumps(VALUE_DICTIONARY), "exception": error_raised})

    @async_test
    async def test_invalid_timeout(self):
        with self.assertRaises(ValueError):
            redis_cache.RedisCache(REDIS_HOST, REDIS_PORT, -1)

    @staticmethod
    def _generate_key():
        return ODS_CODE + "-" + INTERACTION_ID
