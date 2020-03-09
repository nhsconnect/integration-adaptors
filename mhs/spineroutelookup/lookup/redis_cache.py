import asyncio
import json
from typing import Dict, Optional

import redis
from utilities import integration_adaptors_logger as log, timing

from lookup import cache_adaptor

logger = log.IntegrationAdaptorsLogger(__name__)


class RedisCache(cache_adaptor.CacheAdaptor):

    def __init__(self, redis_host: str, redis_port: int, expiry_time: float = cache_adaptor.FIFTEEN_MINUTES_IN_SECONDS,
                 use_tls: bool = True):
        """Initialise a new RedisCache.

        :param redis_host: The Redis host to use for caching.
        :param redis_port: The port on which to connect to the Redis host.
        :param expiry_time: The expiry time (in seconds) to set for cache entries.
        :param use_tls: Whether or not to use TLS when connecting to the Redis host.
        """
        if expiry_time < 0:
            raise ValueError('Expiry time must not be non-negative')

        self.expiry_time = expiry_time

        self._redis_client = redis.Redis(host=redis_host, port=redis_port, ssl=use_tls)
        logger.info("Redis client configured. {host}, {port}, {ssl}",
                    fparams={"host": redis_host, "port": redis_port, "ssl": use_tls})

    @timing.time_function
    async def retrieve_mhs_attributes_value(self, ods_code: str, interaction_id: str) -> Optional[Dict]:
        """
        Returns a value for the given ods code/interaction id. Returns None if the key is expired, not found, maps to a
        a value that cannot be interpreted or there is an error communicating with the Redis cache.

        :param ods_code: The ODS code the value belongs to. Used to construct the Redis key.
        :param interaction_id: The interaction ID code the value belongs to. Used to construct the Redis key.
        :return The cached value, or None if it could not be retrieved.
        """
        key = RedisCache._generate_key(ods_code, interaction_id)

        event_loop = asyncio.get_event_loop()
        try:
            logger.info("Attempting to retrieve cache entry for {key}", fparams={"key": key})
            cached_json_value = await event_loop.run_in_executor(None, self._redis_client.get, key)

            if cached_json_value is None:
                logger.info("No cache entry found for {key}.", fparams={"key": key})
                return None

            value = json.loads(cached_json_value)

            logger.info("Retrieved cache entry for {key}. {value}", fparams={"key": key, "value": value})

            return value
        except redis.RedisError as re:
            logger.exception("An error occurred when attempting to load {key}.", fparams={"key": key})
            raise re

    @timing.time_function
    async def add_cache_value(self, ods_code: str, interaction_id: str, value: Dict) -> None:
        """
        Adds a value to the cache. Does not raise any exceptions if errors are encountered.

        :param ods_code: The ODS code the value belongs to. Used to construct the Redis key.
        :param interaction_id: The interaction ID code the value belongs to. Used to construct the Redis key.
        :param value: The value to be cached.
        """
        key = RedisCache._generate_key(ods_code, interaction_id)

        # Store the dictionary as a JSON string, since Redis doesn't support maps with non-string values.
        json_value = json.dumps(value)

        event_loop = asyncio.get_event_loop()
        try:
            logger.info("Attempting to store {value} in the cache using {key}",
                        fparams={"value": json_value, "key": key})
            await event_loop.run_in_executor(None, self._redis_client.setex, key, self.expiry_time, json_value)
            logger.info("Successfully stored {value} in the cache using {key}",
                        fparams={"value": json_value, "key": key})
        except redis.RedisError as re:
            logger.exception("An error occurred when caching {value}.", fparams={"value": json_value})
            raise re

    @staticmethod
    def _generate_key(ods_code: str, interaction_id: str) -> str:
        return ods_code + '-' + interaction_id
