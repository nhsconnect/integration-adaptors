import abc
import contextlib
import json
from typing import Optional

import aioboto3 as aioboto3

from persistence.dynamo_persistence_adaptor import RecordCreationError
from sequence.sequence import SequenceGenerator
import utilities.integration_adaptors_logger as log
from utilities import config

logger = log.IntegrationAdaptorsLogger(__name__)


class DynamoSequenceGenerator(SequenceGenerator):

    def __init__(self, table_name):
        """
        Constructs a DynamoDB version of a
        :class:`SequenceGenerator <nhais.sequence.SequenceGenerator>`.
        The kwargs provided should contain the following information:
          * table_name: The Table Name used to identify the dynamo table containing required items.
        :param table_name: Table name to be used in this adaptor.
        """
        self.table_name = table_name

    async def next(self, key: str) -> Optional[dict]:
        logger.info('Adding data for {key}', fparams={'key': key})
        try:
            async with self.__get_dynamo_table() as table:
                response = await table.update_item(
                    Key={'key': key},
                    UpdateExpression='set counter = counter + :i',
                    ExpressionAttributeValues={':i': 1},
                    ReturnValues='UPDATED_NEW'
                )
            if response.get('Attributes', {}).get('data') is None:
                logger.info('No previous record found: {key}', fparams={'key': key})
                return None
            return json.loads(response.get('Attributes', {}).get('data'))
        except Exception as e:
            logger.exception('Error creating record')
            raise RecordCreationError from e
        pass

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