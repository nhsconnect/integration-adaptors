"""Module containing functionality for a DynamoDB implementation of a persistence adaptor."""
import contextlib
import json

import aioboto3
import utilities.integration_adaptors_logger as log
from utilities import config

from mhs_common.state import persistence_adaptor

logger = log.IntegrationAdaptorsLogger(__name__)


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

    CLIENT = None

    def __init__(self, table_name):
        """
        Constructs a DynamoDB version of a
        :class:`PersistenceAdaptor <mhs.common.state.persistence_adaptor.PersistenceAdaptor>`.
        The kwargs provided should contain the following information:
          * table_name: The Table Name used to identify the dynamo table containing required items.
        :param table_name: Table name to be used in this adaptor.
        """
        self.table_name = table_name
        if DynamoPersistenceAdaptor.CLIENT is None:
            DynamoPersistenceAdaptor.CLIENT = aioboto3.client('dynamodb', region_name='eu-west-2', endpoint_url=config.get_config('DYNAMODB_ENDPOINT_URL'))

    async def add(self, key, data):
        """Add an item to a specified table, using a provided key.

        :param key: The key used to identify the item.
        :param data: The item to store in persistence.
        :return: The previous version of the item which has been replaced. (None if no previous item)
        """
        logger.info('Adding data for {key}', fparams={'key': key})
        try:
            # table = await self.__get_dynamo_table()
            response = await DynamoPersistenceAdaptor.CLIENT.put_item(
                TableName=self.table_name,
                Item={'key': {'S': key}, 'data': {'S': json.dumps(data)}},
                ReturnValues='ALL_OLD'
            )
            if response.get('Attributes', {}).get('data') is None:
                logger.info('No previous record found: {key}', fparams={'key': key})
                return None
            return json.loads(response.get('Attributes', {}).get('data').get('S'))
            # return json.loads(response.get('Attributes', {}).get('data'))
        except Exception as e:
            logger.exception('Error creating record')
            raise RecordCreationError from e

    async def get(self, key):
        """
        Retrieves an item from a specified table with a given key.
        :param key: The key which identifies the item to get.
        :return: The item from the specified table with the given key. (None if no item found)
        """
        logger.info('Getting record for {key}', fparams={'key': key})
        try:
            # table = await self.__get_dynamo_table()
            response = await DynamoPersistenceAdaptor.CLIENT.get_item(
                TableName=self.table_name,
                Key={'key': {'S': key}}
            )

            if 'Item' not in response:
                logger.info('No item found for record: {key}', fparams={'key': key})
                return None
            return json.loads(response.get('Item', {}).get('data').get('S'))
            # return json.loads(response.get('Item', {}).get('data'))
        except Exception as e:
            logger.exception('Error getting record')
            raise RecordRetrievalError from e

    async def delete(self, key):
        """
        Removes an item from a table given it's key.
        :param key: The key of the item to delete.
        :return: The instance of the item which has been deleted from persistence. (None if no item found)
        """
        logger.info('Deleting record for {key}', fparams={'key': key})
        try:
            # table = await self.__get_dynamo_table()
            response = await DynamoPersistenceAdaptor.CLIENT.delete_item(
                TableName=self.table_name,
                Key={'key': {'S': key}},
                ReturnValues='ALL_OLD'
            )
            if 'Attributes' not in response:
                logger.info('No values found for record: {key}', fparams={'key': key})
                return None
            return json.loads(response.get('Attributes', {}).get('data').get('S'))
            # return json.loads(response.get('Attributes', {}).get('data'))
        except Exception as e:
            logger.exception('Error deleting record')
            raise RecordDeletionError from e

    # @contextlib.asynccontextmanager
    # async def __get_dynamo_table(self):
    #     """
    #     Creates a connection to the table referenced by this instance.
    #     :return: The table to be used by this instance.
    #     """
    #     if self.table_name in tables:
    #         return tables[self.table_name]
    #     resource = await aioboto3.resource('dynamodb', region_name='eu-west-2',
    #                                  endpoint_url=config.get_config('DYNAMODB_ENDPOINT_URL', None))
    #     logger.info('Establishing connection to {table_name}', fparams={'table_name': self.table_name})
    #     return resource.Table(self.table_name)
