import unittest.mock

import redis
from utilities.test_utilities import async_test

from lookup import redis_cache

REDIS_HOST = "host"
REDIS_PORT = 1234
USE_TLS = False

ODS_CODE = "ods"
INTERACTION_ID = "interaction-id"
CACHE_KEY = ODS_CODE + "-" + INTERACTION_ID

VALUE_DICTIONARY = {
    "key1": "value1",
    "key2": ["list_entry_1", "list_entry_2"],
    "key3": {
        "nested_key_1": "nested_value_1",
        "nested_key_2": "nested_value_2"
    }
}

VALUE_DICTIONARY_JSON = '{"key1": "value1", "key2": ["list_entry_1", "list_entry_2"], "key3": {' \
                        '"nested_key_1": "nested_value_1", "nested_key_2": "nested_value_2"}}'

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

    def test_redis_params_are_passed(self):
        redis_cache.RedisCache(REDIS_HOST, REDIS_PORT, use_tls=USE_TLS)

        self.mock_redis_constructor.assert_called_with(host=REDIS_HOST, port=REDIS_PORT, ssl=USE_TLS)

    def test_tls_is_enabled_by_default(self):
        redis_cache.RedisCache(REDIS_HOST, REDIS_PORT)

        self.mock_redis_constructor.assert_called_with(host=REDIS_HOST, port=REDIS_PORT, ssl=True)

    @async_test
    async def test_should_retrieve_value_from_store_if_exists(self):
        cache = redis_cache.RedisCache(REDIS_HOST, REDIS_PORT)
        self.mock_redis.get.return_value = VALUE_DICTIONARY_JSON.encode()

        value = await cache.retrieve_mhs_attributes_value(ODS_CODE, INTERACTION_ID)

        self.assertEqual(value, VALUE_DICTIONARY)
        self.mock_redis.get.assert_called_with(CACHE_KEY)

    @async_test
    async def test_should_return_none_if_value_does_not_exist(self):
        cache = redis_cache.RedisCache(REDIS_HOST, REDIS_PORT)
        self.mock_redis.get.return_value = None

        value = await cache.retrieve_mhs_attributes_value(ODS_CODE, INTERACTION_ID)

        self.assertIsNone(value)

    @async_test
    async def test_should_raise_exception_if_fails_to_retrieve_value(self):
        cache = redis_cache.RedisCache(REDIS_HOST, REDIS_PORT)
        self.mock_redis.get.side_effect = redis.RedisError

        with (self.assertRaises(redis.RedisError)):
            await cache.retrieve_mhs_attributes_value(ODS_CODE, INTERACTION_ID)

    @async_test
    async def test_should_store_value_as_json(self):
        cache = redis_cache.RedisCache(REDIS_HOST, REDIS_PORT)

        await cache.add_cache_value(ODS_CODE, INTERACTION_ID, VALUE_DICTIONARY)

        self.mock_redis.setex.assert_called_with(CACHE_KEY, FIFTEEN_MINUTES_IN_SECONDS,
                                                 VALUE_DICTIONARY_JSON)

    @async_test
    async def test_store_should_use_custom_expiry_time_if_specified(self):
        custom_expiry_time = 27
        cache = redis_cache.RedisCache(REDIS_HOST, REDIS_PORT, expiry_time=custom_expiry_time)

        await cache.add_cache_value(ODS_CODE, INTERACTION_ID, VALUE_DICTIONARY)

        self.mock_redis.setex.assert_called_with(CACHE_KEY, custom_expiry_time, VALUE_DICTIONARY_JSON)

    @async_test
    async def test_store_should_propagate_redis_error_to_caller(self):
        cache = redis_cache.RedisCache(REDIS_HOST, REDIS_PORT)
        self.mock_redis.setex.side_effect = redis.RedisError()

        with self.assertRaises(redis.RedisError):
            await cache.add_cache_value(ODS_CODE, INTERACTION_ID, VALUE_DICTIONARY)

    @async_test
    async def test_should_only_accept_positive_expiry_times(self):
        with self.assertRaises(ValueError):
            redis_cache.RedisCache(REDIS_HOST, REDIS_PORT, -1)
