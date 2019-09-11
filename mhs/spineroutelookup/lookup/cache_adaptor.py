"""This module defines the cache adaptor interface, used to allow support for multiple message configuration caching
implementations."""

from __future__ import annotations

import abc
from typing import Optional, Dict, Type

FIFTEEN_MINUTES_IN_SECONDS = 900

implementations: Dict[str, Type[CacheAdaptor]] = {}


class CacheAdaptor(abc.ABC):
    """An adaptor that provides a common interface to the message configuration cache."""

    def __init__(self, expiry_time=FIFTEEN_MINUTES_IN_SECONDS):
        """
        :param expiry_time: Time for a value to expire in seconds
        """
        if expiry_time < 0:
            raise ValueError('Expiry time must not be non-negative')
        self.expiry_time = expiry_time

    @abc.abstractmethod
    async def retrieve_mhs_attributes_value(self, ods_code: str, interaction_id: str) -> Optional[Dict]:
        """
        Given a key, the cache should return either the cached value or None if the value is not found or if the value
        is out of date
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def add_cache_value(self, ods_code: str, interaction_id: str, value: Dict) -> None:
        """
        Adds a value to the cache, recording the input time used to determine when values have expired
        """
        raise NotImplementedError()
