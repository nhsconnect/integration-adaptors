"""
This module defines the state adapter interface, used to allow support for multiple state database implementations.
"""
from typing import Optional


class PersistenceAdapter:
    """An adapter that provides a common interface to the state management database."""
    pass

    async def add(self, table_name, key, item: dict) -> Optional[dict]:
        """Add an item to a specified table, using a provided key.

        :param table_name: The name of the table to add the item to.
        :param key: The key used to identify the item.
        :param item: The item to store in persistence.
        :return: The previous version of the item which has been replaced. (None if no previous item)
        """
        pass

    async def get(self, table_name, key) -> Optional[dict]:
        """
        Retrieves an item from a specified table with a given key.
        :param table_name: The table to use when finding the item.
        :param key: The key which identifies the item to get.
        :return: The item from the specified table with the given key. (None if no item found)
        """
        pass

    async def delete(self, table_name, key) -> Optional[dict]:
        """
        Removes an item from a table given it's key.
        :param table_name: The table to delete the item from.
        :param key: The key of the item to delete.
        :return: The instance of the item which has been deleted from persistence. (None if no item found)
        """
        pass
