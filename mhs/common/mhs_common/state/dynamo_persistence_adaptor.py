"""Module containing functionality for a DynamoDB implementation of a persistence adaptor."""
import contextlib
import json
import traceback

import aioboto3
import utilities.integration_adaptors_logger as log
from utilities import config

from mhs_common.state import persistence_adaptor

logger = log.IntegrationAdaptorsLogger('DYNAMO_PERSISTENCE')


class RecordCreationError(RuntimeError):
    """Error occurred when creating record."""
    pass


class RecordDeletionError(RuntimeError):
    """Error occurred when deleting record."""
    pass


class RecordRetrievalError(RuntimeError):
    """Error occurred when retrieving record."""
    pass


class DynamoPersistenceAdaptor(persistence_adaptor.PersistenceAdaptor):
    """Class responsible for persisting items into a DynamoDB."""

    def __init__(self, **kwargs):
        """
        Constructs a DynamoDB version of a
        :class:`PersistenceAdaptor <mhs.common.state.persistence_adaptor.PersistenceAdaptor>`.
        The kwargs provided should contain the following information:
          * table_name: The Table Name used to identify the dynamo table containing required items.
        :param kwargs: The key word arguments required for this constructor.
        """
        self.table_name = kwargs.get('table_name')

    async def add(self, key, data):
        """Add an item to a specified table, using a provided key.

        :param key: The key used to identify the item.
        :param data: The item to store in persistence.
        :return: The previous version of the item which has been replaced. (None if no previous item)
        """
        logger.info('011', 'Adding {record} for {key}', {'record': data, 'key': key})
        try:
            async with self.__create_dynamo_table() as table:
                response = await table.put_item(
                    Item={'key': key, 'data': json.dumps(data)},
                    ReturnValues='ALL_OLD'
                )
            if response.get('Attributes', {}).get('data') is None:
                logger.info('000', 'No previous record found: {key}', {'key': key})
                return None
            return json.loads(response.get('Attributes', {}).get('data'))
        except Exception as e:
            logger.error('001', 'Error creating record: {exception}', {'exception': traceback.format_exc()})
            raise RecordCreationError from e

    async def get(self, key):
        """
        Retrieves an item from a specified table with a given key.
        :param key: The key which identifies the item to get.
        :return: The item from the specified table with the given key. (None if no item found)
        """
        logger.info('002', 'Getting record for {key}', {'key': key})
        try:
            async with self.__create_dynamo_table() as table:
                response = await table.get_item(
                    Key={'key': key}
                )
            logger.info('003', 'Response from get_item call: {response}', {'response': response})
            if 'Item' not in response:
                logger.info('004', 'No item found for record: {key}', {'key': key})
                return None
            return json.loads(response.get('Item', {}).get('data'))
        except Exception as e:
            logger.error('005', 'Error getting record: {exception}', {'exception': traceback.format_exc()})
            raise RecordRetrievalError from e

    async def delete(self, key):
        """
        Removes an item from a table given it's key.
        :param key: The key of the item to delete.
        :return: The instance of the item which has been deleted from persistence. (None if no item found)
        """
        logger.info('006', 'Deleting record for {key}', {'key': key})
        try:
            async with self.__create_dynamo_table() as table:
                response = await table.delete_item(
                    Key={'key': key},
                    ReturnValues='ALL_OLD'
                )
            logger.info('007', 'Response from delete_item call: {response}', {'response': response})
            if 'Attributes' not in response:
                logger.info('008', 'No values found for record: {key}', {'key': key})
                return None
            return json.loads(response.get('Attributes', {}).get('data'))
        except Exception as e:
            logger.error('009', 'Error deleting record: {exception}', {'exception': traceback.format_exc()})
            raise RecordDeletionError from e

    @contextlib.asynccontextmanager
    async def __create_dynamo_table(self):
        """
        Creates a connection to the table referenced by this instance.
        :return: The table to be used by this instance.
        """
        async with aioboto3.resource('dynamodb', region_name='eu-west-2',
                                     endpoint_url=config.get_config('DYNAMODB_ENDPOINT_URL', None)) as dynamo_resource:
            logger.info('010', 'Establishing connection to {table_name}', {'table_name': self.table_name})
            yield dynamo_resource.Table(self.table_name)
