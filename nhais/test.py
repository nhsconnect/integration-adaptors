import asyncio

import aioboto3
import botocore.errorfactory
from boto3.dynamodb.conditions import Key

import sequence.dynamo_sequence
from sequence.dynamo_sequence import DynamoSequenceGenerator
from utilities import config
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


async def init_first_item(table_name: str, key: str):
    endpoint = config.get_config('DYNAMODB_ENDPOINT_URL', None)
    async with aioboto3.resource('dynamodb', region_name='eu-west-2', endpoint_url=endpoint) as dynamo_resource:
        try:
            await dynamo_resource.create_table(
                AttributeDefinitions=[
                                         {'AttributeName': 'key', 'AttributeType': 'S'}
                                     ],
                KeySchema=[
                              {'AttributeName': 'key', 'KeyType': 'HASH'}
                          ],
                ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
                TableName=table_name
            )
        except dynamo_resource.meta.client.exceptions.ResourceInUseException:
            logger.info(f'Cannot create table {table_name}: table already exists')
            pass

        table = await dynamo_resource.Table(table_name)

        result = await table.query(
            KeyConditionExpression=Key('key').eq(key)
        )

        print('============ init_first_item ===========')
        print(result)
        if result['Count'] == 0:
            await table.put_item(
                Item={'key': key, sequence.dynamo_sequence._COUNTER_ATTRIBUTE: 9999990}
            )


async def main():
    table = 'transaction_id_counter'
    key = 'transaction_id'
    db = sequence.dynamo_sequence.DynamoSequenceGenerator(table)
    # TODO: We can't be doing this for every sequence number!
    await init_first_item(table, key)
    transaction_id = await db.next(key)
    print(f'TRANSACTION ID!!!     {transaction_id}')


if __name__ == '__main__':
    config.setup_config("MHS")
    log.configure_logging("MHS")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
