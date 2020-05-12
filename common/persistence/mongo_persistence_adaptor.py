"""Module containing functionality for a DynamoDB implementation of a persistence adaptor."""
import copy
import threading

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

import utilities.integration_adaptors_logger as log
from persistence import persistence_adaptor
from persistence.persistence_adaptor import retriable, RecordCreationError, RecordUpdateError, RecordRetrievalError, \
    RecordDeletionError
from utilities import config

logger = log.IntegrationAdaptorsLogger(__name__)

_DB_NAME = 'integration-adaptors'
_KEY = "_id"


class MongoPersistenceAdaptor(persistence_adaptor.PersistenceAdaptor):
    """Class responsible for persisting items into a MongoDB."""

    client = None

    def __init__(self, table_name: str, max_retries: int, retry_delay: float):
        """
        Constructs a DynamoDB version of a
        :class:`PersistenceAdaptor <mhs.common.state.persistence_adaptor.PersistenceAdaptor>`.
        The kwargs provided should contain the following information:
          * table_name: The Table Name used to identify the dynamo table containing required items.
          * max_retries: The number of max retries object should make if there is an error connecting with the DB
          * retry_delay: The delay between retries
        :param table_name: Table name to be used in this adaptor.
        """
        self.table_name = table_name
        self.retry_delay = retry_delay
        self.max_retries = max_retries

        client = MongoPersistenceAdaptor._initialize_mongo_client()
        self.collection = client[_DB_NAME][table_name]

    @retriable
    async def add(self, key, data):
        """Add an item to a specified table, using a provided key.

        :param key: The key under which to store the data in persistence.
        :param data: The item to store in persistence.
        """

        if _KEY in data:
            raise ValueError(f"Added data must not have field named '{_KEY}' as it's used "
                             f"as primary key and is explicitly set as this function argument")

        logger.info('Adding data for {key} in table {table}', fparams={'key': key, 'table': self.table_name})

        try:
            result = await self.collection.insert_one(self._prepare_data_to_add(key, data))
            if not result.acknowledged:
                raise RecordCreationError
        except Exception as e:
            raise RecordCreationError from e

    @retriable
    async def update(self, key: str, data: dict):
        """Updates an item in a specified table, using a provided key.

        :param key: The key used to identify the item.
        :param data: The item to update in persistence.
        :return: The previous version of the item which has been replaced. (None if no previous item)
        """

        if _KEY in data:
            raise ValueError(f"Added data must not have field named '{_KEY}' as it's used "
                             f"as primary key and is explicitly set as this function argument")

        logger.info('Updating data for {key} in table {table}', fparams={'key': key, 'table': self.table_name})

        try:
            result = await self.collection.find_one_and_update(
                {_KEY: key},
                {'$set': data},
                return_document=ReturnDocument.AFTER)
            return self._prepare_data_to_return(result)
        except Exception as e:
            raise RecordUpdateError from e

    @retriable
    async def get(self, key: str, **kwargs):
        """
        Retrieves an item from a specified table with a given key.
        :param key: The key which identifies the item to get.
        :param strongly_consistent_read: https://docs.amazonaws.cn/en_us/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html
        :return: The item from the specified table with the given key. (None if no item found)
        """
        logger.info('Getting record for {key} from table {table}', fparams={'key': key, 'table': self.table_name})
        try:
            result = await self.collection.find_one({_KEY: key})
            return self._prepare_data_to_return(result)
        except Exception as e:
            raise RecordRetrievalError from e

    @retriable
    async def delete(self, key):
        """
        Removes an item from a table given it's key.
        :param key: The key of the item to delete.
        :return: The instance of the item which has been deleted from persistence. (None if no item found)
        """
        logger.info('Deleting record for {key} from table {table}', fparams={'key': key, 'table': self.table_name})
        try:
            result = await self.collection.find_one_and_delete({_KEY: key})
            return self._prepare_data_to_return(result)
        except Exception as e:
            raise RecordDeletionError from e

    @staticmethod
    def _prepare_data_to_add(key, data):
        item = copy.deepcopy(data)
        item[_KEY] = key
        return item

    @staticmethod
    def _prepare_data_to_return(data):
        if data is not None:
            del data[_KEY]
        return data

    @staticmethod
    def _initialize_mongo_client():
        with threading.Lock():
            if MongoPersistenceAdaptor.client is None:
                MongoPersistenceAdaptor.client = AsyncIOMotorClient(config.get_config('MONGODB_ENDPOINT_URL'))
        return MongoPersistenceAdaptor.client
