"""
This module defines the state adaptor interface, used to allow support for multiple state database implementations.
"""
import abc
from typing import Optional


class PersistenceAdaptor(abc.ABC):
    """An adaptor that provides a common interface to a specific item type in a database."""

    @abc.abstractmethod
    async def add(self, key: str, data: dict) -> Optional[dict]:
        """Add an item to a specified table, using a provided key.

        :param key: The key used to identify the item.
        :param data: The item to store in persistence.
        :return: The previous version of the item which has been replaced. (None if no previous item)
        """
        pass

    @abc.abstractmethod
    async def get(self, key: str) -> Optional[dict]:
        """
        Retrieves an item from a specified table with a given key.
        :param key: The key which identifies the item to get.
        :return: The item from the specified table with the given key. (None if no item found)
        """
        pass

    @abc.abstractmethod
    async def delete(self, key: str) -> Optional[dict]:
        """
        Removes an item from a table given it's key.
        :param key: The key of the item to delete.
        :return: The instance of the item which has been deleted from persistence. (None if no item found)
        """
        pass