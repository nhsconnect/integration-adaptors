"""This module defines the cache adapter interface, used to allow support for multiple message configuration caching
implementations."""

FIFTEEN_MINUTES_IN_SECONDS = 900


class CacheAdapter:
    """An adapter that provides a common interface to the message configuration cache."""

    def __init__(self, expiry_time=FIFTEEN_MINUTES_IN_SECONDS):
        """
        :param expiry_time: Time for a value to expire in seconds
        """
        pass

    async def retrieve_mhs_attributes_value(self, ods_code: str, interaction_id: str) -> Optional[Dict]:
        """
        Given a key, the cache should return either the cached value or None if the value is not found or if the value
        is out of date
        """
        pass

    @abc.abstractmethod
    async def add_cache_value(self, ods_code: str, interaction_id: str, value: Dict) -> None:
        """
        Adds a value to the cache, recording the input time used to determine when values have expired
        """
        pass
