"""Module containing functionality for a DynamoDB implementation of a persistence adaptor."""
import contextlib
import copy

import aioboto3
from boto3.dynamodb.conditions import Attr

import utilities.integration_adaptors_logger as log
from persistence import persistence_adaptor
from persistence.persistence_adaptor import retriable, RecordCreationError, RecordUpdateError, RecordRetrievalError, \
    RecordDeletionError, validate_data
from utilities import config

logger = log.IntegrationAdaptorsLogger(__name__)

_KEY = "key"


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
        self.table_name = table_name
        self.retry_delay = retry_delay
        self.max_retries = max_retries

        self.endpoint_url = config.get_config('DB_ENDPOINT_URL', None)
        self.region_name = 'eu-west-2'

    @validate_data(primary_key=_KEY)
    @retriable
    async def add(self, key, data):
        """Add an item to a specified table, using a provided key.

        :param key: The key under which to store the data in persistence.
        :param data: The item to store in persistence.
        """

        logger.info('Adding data for {key} in table {table}', fparams={'key': key, 'table': self.table_name})

        try:
            async with self.__get_dynamo_table() as table:
                await table.put_item(
                    Item=self._prepare_data_to_add(key, data),
                    ConditionExpression=Attr(_KEY).not_exists())
        except Exception as e:
            raise RecordCreationError from e

    @validate_data(primary_key=_KEY)
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
                    Key={_KEY: key},
                    AttributeUpdates=attribute_updates,
                    ReturnValues="ALL_NEW")

            return self._prepare_data_to_return(response.get('Attributes', {}))
        except Exception as e:
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
                    Key={_KEY: key},
                    ConsistentRead=strongly_consistent_read)

            if 'Item' not in response:
                logger.info('No item found for record: {key} in table {table}', fparams={'key': key, 'table': self.table_name})
                return None
            attributes = response.get('Item', {})
            return self._prepare_data_to_return(attributes)
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
                    Key={_KEY: key},
                    ReturnValues='ALL_OLD'
                )
            if 'Attributes' not in response:
                logger.info('No values found for {key} in table {table}', fparams={'key': key, 'table': self.table_name})
                return None
            attributes = response.get('Attributes', {})
            return self._prepare_data_to_return(attributes)
        except Exception as e:
            raise RecordDeletionError from e

    @contextlib.asynccontextmanager
    async def __get_dynamo_table(self):
        """
        Creates a connection to the table referenced by this instance.
        :return: The table to be used by this instance.
        """
        async with aioboto3.resource('dynamodb',
                                     region_name=self.region_name,
                                     endpoint_url=self.endpoint_url) as dynamo_resource:
            logger.info('Establishing connection to {table_name}', fparams={'table_name': self.table_name})
            yield dynamo_resource.Table(self.table_name)

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
