"""Module to test dynamo sequence functionality."""
import unittest

import aioboto3
from sequence import dynamo_sequence
from utilities import test_utilities
from utilities import config


class TestDynamoSequence(unittest.TestCase):

    def setUp(self):
        config.setup_config("MHS")
        self.table_name = 'test_dynamo_sequence_table'
        self.key = 'transaction_id'
        self.endpoint = config.get_config('DYNAMODB_ENDPOINT_URL', None)
        self.region_name = 'eu-west-2'

    @test_utilities.async_test
    async def test_transaction_ids_increase_by_one(self):
        async with aioboto3.resource('dynamodb', region_name=self.region_name,
                                     endpoint_url=self.endpoint) as dynamo_resource:
            try:
                await self.create_table(dynamo_resource)
                db = dynamo_sequence.DynamoSequenceGenerator(self.table_name)
                transaction_id_1 = await db.next(self.key)
                transaction_id_2 = await db.next(self.key)
                self.assertEqual(transaction_id_1 + 1, transaction_id_2)
            except dynamo_resource.meta.client.exceptions.ResourceInUseException:
                self.fail()
            finally:
                table = await dynamo_resource.Table(self.table_name)
                await table.delete()

    @test_utilities.async_test
    async def test_first_transaction_id_should_be_one(self):
        async with aioboto3.resource('dynamodb', region_name=self.region_name,
                                     endpoint_url=self.endpoint) as dynamo_resource:
            try:
                await self.create_table(dynamo_resource)
                db = dynamo_sequence.DynamoSequenceGenerator(self.table_name)
                transaction_id = await db.next(self.key)
                self.assertEqual(transaction_id, 1)
            except dynamo_resource.meta.client.exceptions.ResourceInUseException:
                self.fail()
            finally:
                table = await dynamo_resource.Table(self.table_name)
                await table.delete()

    @test_utilities.async_test
    async def test_after_9999999_should_be_one(self):
        async with aioboto3.resource('dynamodb', region_name=self.region_name,
                                     endpoint_url=self.endpoint) as dynamo_resource:
            try:
                await self.create_table(dynamo_resource)
                db = dynamo_sequence.DynamoSequenceGenerator(self.table_name)
                table = await dynamo_resource.Table(self.table_name)
                await table.put_item(
                    Item={'key': self.key, dynamo_sequence._COUNTER_ATTRIBUTE: 9999999}
                )
                transaction_id = await db.next(self.key)
                self.assertEqual(transaction_id, 1)
            except dynamo_resource.meta.client.exceptions.ResourceInUseException:
                self.fail()
            finally:
                await table.delete()

    async def create_table(self, dynamo_resource):
        await dynamo_resource.create_table(
            AttributeDefinitions=[
                {'AttributeName': 'key', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'key', 'KeyType': 'HASH'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
            TableName=self.table_name
        )
