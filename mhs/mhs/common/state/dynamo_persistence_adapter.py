import json
import traceback

import aioboto3
import utilities.integration_adaptors_logger as log

import mhs.common.state.persistence_adapter

logger = log.IntegrationAdaptorsLogger('DYNAMO_PERSISTENCE')


class RecordCreationError(RuntimeError):
    def __init__(self):
        pass


class RecordDeletionError(RuntimeError):
    def __init__(self):
        pass


class RecordRetrievalError(RuntimeError):
    def __init__(self):
        pass


class InvalidTableError(RuntimeError):
    def __init__(self):
        pass


class DynamoPersistenceAdapter(mhs.common.state.persistence_adapter.PersistenceAdapter):
    """
    Class responsible for persisting items into DynamoDB.
    """

    def __init__(self, **kwargs):
        """
        Constructs a DynamoDB version of a
        :class:`PersistenceAdapter <mhs.common.state.persistence_adapter.PersistenceAdapter>`.
        The kwargs provided should contain the following information:
          * state_table: The name used to refer to the table containing state items.
          * state_arn: The Amazon Resource Name used to identify the dynamo table containing state items.
          * sync_async_table: The name used to refer to the table containing sync_async message items.
          * sync_async_arn: The Amazon Resource Name used to identify the dynamo table containing sync_async message
            items.
        :param kwargs: The key word arguments required for this constructor.
        """
        state_table = kwargs.get('state_table', 'state')
        state_arn = kwargs.get('state_arn')
        sync_async_table = kwargs.get('sync_async_table', 'sync_async')
        sync_async_arn = kwargs.get('sync_async_arn')

        dynamo_db = aioboto3.resource('dynamodb')

        self.tables = {
            state_table: dynamo_db.Table(state_arn),
            sync_async_table: dynamo_db.Table(sync_async_arn)
        }

    async def add(self, table_name, key, item):
        logger.info('011', 'Adding {record} for {key}', {'record': item, 'key': key})
        try:
            response = await self._resolve_table(table_name).put_item(
                Item={'key': key, 'data': json.dumps(item)},
                ReturnValues='ALL_OLD'
            )
            if 'Attributes' not in response or response.get('Attributes', {}).get('data') is None:
                logger.info('000', 'No previous record found: {key}', {'key': key})
                return None
            return json.loads(response.get('Attributes', {}).get('data'))
        except Exception as e:
            logger.error('001', 'Error creating record: {exception}', {'exception': traceback.format_exc()})
            raise RecordCreationError from e

    async def get(self, table_name, key):
        logger.info('002', 'Getting record for {key}', {'key': key})
        try:
            response = await self._resolve_table(table_name).get_item(
                Key=key
            )
            logger.info('003', 'Response from get_item call: {response}', {'response': response})
            if 'Item' not in response:
                logger.info('004', 'No item found for record: {key}', {'key': key})
                return None
            return json.loads(response.get('Item', {}).get('data'))
        except Exception as e:
            logger.error('005', 'Error getting record: {exception}', {'exception': traceback.format_exc()})
            raise RecordRetrievalError from e

    async def delete(self, table_name, key):
        logger.info('006', 'Deleting record for {key}', {'key': key})
        try:
            response = await self._resolve_table(table_name).delete_item(
                Key=key,
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

    def _resolve_table(self, table_name):
        table = self.tables.get(table_name)
        if table is None:
            logger.info('010', 'Table could not be found for: {table_name}', {'table_name': table_name})
            raise InvalidTableError
        return table
