"""Module to test dynamo sequence functionality."""
import unittest

import aioboto3
from sequence import dynamo_sequence
from utilities import test_utilities
from utilities import config


class TestDynamoSequence(unittest.TestCase):

    def setUp(self):
        config.setup_config("MHS")
        self.table_name = 'transaction_id_counter'
        self.key = 'transaction_id'
        self.endpoint = config.get_config('DYNAMODB_ENDPOINT_URL', None)


    @test_utilities.async_test
    async def test_transaction_ids_increase_by_one(self):
        async def test_first_transaction_id_should_be_one(self):
            async with aioboto3.resource('dynamodb', region_name='eu-west-2',
                                         endpoint_url=self.endpoint) as dynamo_resource:
                try:
                    await dynamo_resource.create_table(
                        AttributeDefinitions=[
                            {'AttributeName': 'key', 'AttributeType': 'S'}
                        ],
                        KeySchema=[
                            {'AttributeName': 'key', 'KeyType': 'HASH'}
                        ],
                        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
                        TableName='test_table'
                    )
                    db = dynamo_sequence.DynamoSequenceGenerator('test_table')
                    transaction_id_1 = await db.next(self.key)
                    transaction_id_2 = await db.next(self.key)
                    self.assertEqual(transaction_id_1 + 1, transaction_id_2)
                except dynamo_resource.meta.client.exceptions.ResourceInUseException:
                    pass
                finally:
                    table = await dynamo_resource.Table('test_table')
                    await table.delete()


    @test_utilities.async_test
    async def test_first_transaction_id_should_be_one(self):
        async with aioboto3.resource('dynamodb', region_name='eu-west-2',
                                     endpoint_url=self.endpoint) as dynamo_resource:
            try:
                await dynamo_resource.create_table(
                    AttributeDefinitions=[
                        {'AttributeName': 'key', 'AttributeType': 'S'}
                    ],
                    KeySchema=[
                        {'AttributeName': 'key', 'KeyType': 'HASH'}
                    ],
                    ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
                    TableName='test_table'
                )
                db = dynamo_sequence.DynamoSequenceGenerator('test_table')
                transaction_id = await db.next(self.key)
                self.assertEqual(transaction_id, 1)
            except dynamo_resource.meta.client.exceptions.ResourceInUseException:
                pass
            finally:
                table = await dynamo_resource.Table('test_table')
                await table.delete()

    @test_utilities.async_test
    async def test_after_9999999_should_be_one(self):
        async with aioboto3.resource('dynamodb', region_name='eu-west-2',
                                     endpoint_url=self.endpoint) as dynamo_resource:
            try:
                await dynamo_resource.create_table(
                    AttributeDefinitions=[
                        {'AttributeName': 'key', 'AttributeType': 'S'}
                    ],
                    KeySchema=[
                        {'AttributeName': 'key', 'KeyType': 'HASH'}
                    ],
                    ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
                    TableName='test_table'
                )
                db = dynamo_sequence.DynamoSequenceGenerator('test_table')
                table = await dynamo_resource.Table('test_table')
                await table.put_item(
                    Item={'key': self.key, dynamo_sequence._COUNTER_ATTRIBUTE: 9999999}
                )
                transaction_id = await db.next(self.key)
                self.assertEqual(transaction_id, 1)
            except dynamo_resource.meta.client.exceptions.ResourceInUseException:
                pass
            finally:
                await table.delete()

