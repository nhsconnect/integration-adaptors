"""
This module defines the state adaptor interface, used to allow support for multiple state database implementations.
"""
import abc
from typing import Optional
import copy
from exceptions import MaxRetriesExceeded
from retry.retriable_action import RetriableAction

DATA_VALIDATION_ERROR_MESSAGE = "Data must not have field named '{}' as it's used " \
                                 "as primary key and is explicitly set as this function argument"


def validate_data_has_no_primary_key_field(primary_key: str):
    def decorator(function):
        async def wrapper(*args, **kwargs):
            _, _, data = args
            if primary_key in data:
                raise ValueError(DATA_VALIDATION_ERROR_MESSAGE.format(primary_key))
            return await function(*args, **kwargs)
        return wrapper
    return decorator


def retriable(func):
    async def inner(*args, **kwargs):
        self = args[0]
        if hasattr(self, 'max_retries') and hasattr(self, 'retry_delay'):
            result = await RetriableAction(func, self.max_retries, self.retry_delay).execute(*args, **kwargs)
            if not result.is_successful:
                raise MaxRetriesExceeded("Max number of retries exceeded when performing DB call") from result.exception
            return result.result
        else:
            raise RuntimeError("Retriable must be set on method which object has 'max_retries: int' and 'retry_delay: float' attributes")
    return inner


class RecordCreationError(RuntimeError):
    """Error occurred when creating record."""
    pass


class RecordDeletionError(RuntimeError):
    """Error occurred when deleting record."""
    pass


class RecordRetrievalError(RuntimeError):
    """Error occurred when retrieving record."""
    pass


class RecordUpdateError(RuntimeError):
    """Error occurred when updating record."""
    pass


class PersistenceAdaptor(abc.ABC):
    """An adaptor that provides a common interface to a specific item type in a database."""

    @abc.abstractmethod
    async def add(self, key: str, data: dict) -> None:
        """Add an item to a specified table, using 'key' from data.

        :param key: The key under which to store the data in persistence.
        :param data: The item to store in persistence. Must have 'key'
        :return: The previous version of the item which has been replaced. (None if no previous item)
        """
        pass

    @abc.abstractmethod
    async def update(self, key: str, data: dict):
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

    @staticmethod
    def add_primary_key_field(primary_key_field, key, data):
        item = copy.deepcopy(data)
        item[primary_key_field] = key
        return item

    @staticmethod
    def remove_primary_key_field(primary_key_field, data):
        if data is not None:
            del data[primary_key_field]
        return data