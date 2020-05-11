"""Module containing functionality for a DynamoDB implementation of a persistence adaptor."""
import contextlib

import aioboto3
from boto3.dynamodb.conditions import Attr

import utilities.integration_adaptors_logger as log
from exceptions import MaxRetriesExceeded
from retry.retriable_action import RetriableAction
from persistence import persistence_adaptor
from utilities import config

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


class RecordUpdateError(RuntimeError):
    """Error occurred when updating record."""
    pass


def retriable(func):
    async def inner(*args, **kwargs):
        self = args[0]
        if hasattr(self, 'max_retries') and hasattr(self, 'retry_delay'):
            result = await RetriableAction(func, self.max_retries, self.retry_delay).execute(*args, **kwargs)
            if not result.is_successful:
                raise MaxRetriesExceeded from result.exception
            return result.result
        else:
            raise RuntimeError("Retriable must be set on method which object has 'max_retries: int' and 'retry_delay: float' attributes")
    return inner


class DynamoPersistenceAdaptor(persistence_adaptor.PersistenceAdaptor):
    """Class responsible for persisting items into a DynamoDB."""

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
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        self.table_name = table_name

    @retriable
    async def add(self, data):
        """Add an item to a specified table, using a provided key.

        :param data: The item to store in persistence.
        """

        if 'key' not in data:
            raise ValueError("Added data should have 'key' as one of it's items")

        logger.info('Adding data for {key} in table {table}', fparams={'key': data['key'], 'table': self.table_name})

        try:
            async with self.__get_dynamo_table() as table:
                await table.put_item(
                    Item=data,
                    ConditionExpression=Attr('key').not_exists())
        except Exception as e:
            raise RecordCreationError from e

    @retriable
    async def update(self, key: str, data: dict):
        """Updates an item in a specified table, using a provided key.

        :param key: The key used to identify the item.
        :param data: The item to update in persistence.
        :return: The previous version of the item which has been replaced. (None if no previous item)
        """
        logger.info('Updating data for {key} in table {table}', fparams={'key': key, 'table': self.table_name})

        attribute_updates = dict([(k, {"Value": v}) for k, v in data.items()])

        try:
            async with self.__get_dynamo_table() as table:
                response = await table.update_item(
                    Key={'key': key},
                    AttributeUpdates=attribute_updates,
                    ReturnValues="ALL_NEW")

            return response.get('Attributes', {})
        except Exception as e:
            logger.exception('Error getting record')
            raise RecordUpdateError from e

    @retriable
    async def get(self, key: str, strongly_consistent_read: bool = False):
        """
        Retrieves an item from a specified table with a given key.
        :param key: The key which identifies the item to get.
        :param strongly_consistent_read: https://docs.amazonaws.cn/en_us/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html
        :return: The item from the specified table with the given key. (None if no item found)
        """
        logger.info('Getting record for {key} from table {table}', fparams={'key': key, 'table': self.table_name})
        try:
            async with self.__get_dynamo_table() as table:
                response = await table.get_item(
                    Key={'key': key},
                    ConsistentRead=strongly_consistent_read)

            if 'Item' not in response:
                logger.info('No item found for record: {key} in table {table}', fparams={'key': key, 'table': self.table_name})
                return None
            attributes = response.get('Item', {})
            return attributes
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
            async with self.__get_dynamo_table() as table:
                response = await table.delete_item(
                    Key={'key': key},
                    ReturnValues='ALL_OLD'
                )
            if 'Attributes' not in response:
                logger.info('No values found for {key} in table {table}', fparams={'key': key, 'table': self.table_name})
                return None
            attributes = response.get('Attributes', {})
            return attributes
        except Exception as e:
            raise RecordDeletionError from e

    @contextlib.asynccontextmanager
    async def __get_dynamo_table(self):
        """
        Creates a connection to the table referenced by this instance.
        :return: The table to be used by this instance.
        """
        async with aioboto3.resource('dynamodb', region_name='eu-west-2',
                                     endpoint_url=config.get_config('DYNAMODB_ENDPOINT_URL', None)) as dynamo_resource:
            logger.info('Establishing connection to {table_name}', fparams={'table_name': self.table_name})
            yield dynamo_resource.Table(self.table_name)
