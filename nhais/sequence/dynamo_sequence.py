import aioboto3 as aioboto3
import utilities.integration_adaptors_logger as log
from utilities import config

from sequence.sequence import SequenceGenerator

logger = log.IntegrationAdaptorsLogger(__name__)

_COUNTER_ATTRIBUTE = 'last_generated_number'
_INCREMENT_EXPRESSION = f'ADD {_COUNTER_ATTRIBUTE} :i'
_INCREMENT_VALUE = {':i': 1}


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

    async def next(self, key: str) -> int:
        num = await self._next(key)
        # zero is never a valid transaction id
        if num == 0:
            num = await self._next(key)
        return num

    async def _next(self, key: str) -> int:
        endpoint = config.get_config('DYNAMODB_ENDPOINT_URL', None)
        async with aioboto3.resource('dynamodb', region_name='eu-west-2', endpoint_url=endpoint) as dynamo_resource:
            table = await dynamo_resource.Table(self.table_name)
            response = await table.update_item(
                Key={'key': key},
                UpdateExpression=_INCREMENT_EXPRESSION,
                ExpressionAttributeValues=_INCREMENT_VALUE,
                ReturnValues='UPDATED_NEW'
            )

            return response['Attributes'][_COUNTER_ATTRIBUTE] % 10000000
