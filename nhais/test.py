import asyncio

import aioboto3
import botocore.errorfactory
from boto3.dynamodb.conditions import Key

import sequence.dynamo_sequence
from sequence.dynamo_sequence import DynamoSequenceGenerator
from utilities import config
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

async def main():
    table = 'transaction_id_counter'
    key = 'transaction_id'
    db = sequence.dynamo_sequence.DynamoSequenceGenerator(table)
    transaction_id = await db.next(key)
    print(f'TRANSACTION ID!!!     {transaction_id}')


if __name__ == '__main__':
    config.setup_config("MHS")
    log.configure_logging("MHS")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
