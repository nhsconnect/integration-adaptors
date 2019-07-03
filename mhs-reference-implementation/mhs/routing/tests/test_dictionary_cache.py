from unittest import TestCase
import mhs.routing.dictionary_cache as Cache
from utilities.test_utilities import async_test
import time


class TestDictionaryCache(TestCase):

    @async_test
    async def test_get_empty_value(self):
        cache = Cache.DictionaryCache()
        value = await cache.retrieve_mhs_attributes_value("ods", "interaction")

        self.assertIsNone(value)

    @async_test
    async def test_get_basic_value(self):
        cache = Cache.DictionaryCache()
        # Check cache is empty first
        self.assertTrue(not cache.cache)

        await cache.add_cache_value("code", "int", "check123")
        value = await cache.retrieve_mhs_attributes_value("code", "int")

        self.assertIsNotNone(value)
        self.assertEqual(value, "check123")

    @async_test
    async def test_timeout(self):
        cache = Cache.DictionaryCache(1)  # Set timeout to 1m
        await cache.add_cache_value("code", "int", "check123")

        value = await cache.retrieve_mhs_attributes_value("code", "int")

        self.assertIsNotNone(value)
        self.assertEqual(value, "check123")

    @async_test
    async def test_message_should_timeout(self):
        half_second = 1.0 / 120
        cache = Cache.DictionaryCache(half_second)
        await cache.add_cache_value("code", "int", "check123")

        time.sleep(1)

        value = await cache.retrieve_mhs_attributes_value("code", "int")

        self.assertIsNone(value)

    @async_test
    async def test_multiple_timeout(self):
        cache = Cache.DictionaryCache(2)
        await cache.add_cache_value("code", "int", "check123")

        time.sleep(1)

        value = await cache.retrieve_mhs_attributes_value("code", "int")
        self.assertEqual(value, "check123")  # Check value in cache

        time.sleep(1.5)  # wait for value to expire in cache

        value = await cache.retrieve_mhs_attributes_value("code", "int")
        self.assertIsNone(value)

    @async_test
    async def test_ttl_does_not_change_on_read(self):
        cache = Cache.DictionaryCache()

        await cache.add_cache_value("code", "int", "check123")
        insert_time = cache.cache['codeint']['time']

        await cache.retrieve_mhs_attributes_value("code", "int")
        self.assertEqual(insert_time, cache.cache['codeint']['time'])

    @async_test
    async def test_invalid_timeout(self):
        with self.assertRaises(ValueError):
            Cache.DictionaryCache(-1)
