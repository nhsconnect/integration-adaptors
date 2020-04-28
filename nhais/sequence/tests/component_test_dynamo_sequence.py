"""Module to test dynamo sequence functionality."""

import unittest
import asyncio

import aioboto3
from sequence import dynamo_sequence
from utilities import test_utilities
from utilities import config


class ComponentTestDynamoSequence(unittest.TestCase):

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
                await self.__create_table(dynamo_resource)
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
                await self.__create_table(dynamo_resource)
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
                await self.__create_table(dynamo_resource)
                table = await dynamo_resource.Table(self.table_name)
                await table.put_item(
                    Item={'key': self.key, dynamo_sequence._COUNTER_ATTRIBUTE: 9999999}
                )
                db = dynamo_sequence.DynamoSequenceGenerator(self.table_name)
                transaction_id = await db.next(self.key)
                self.assertEqual(transaction_id, 1)
            except dynamo_resource.meta.client.exceptions.ResourceInUseException:
                self.fail()
            finally:
                await table.delete()

    @test_utilities.async_test
    async def test_parallel_generation_with_no_gaps_no_duplicates(self):
        async with aioboto3.resource('dynamodb', region_name=self.region_name,
                                     endpoint_url=self.endpoint) as dynamo_resource:
            try:
                await self.__create_table(dynamo_resource)
                db = dynamo_sequence.DynamoSequenceGenerator(self.table_name)
                result = await asyncio.gather(
                    self.__generate_large_number_of_ids("one", 0.05, db),
                    self.__generate_large_number_of_ids("two", 0.075, db)
                )
                await self.__verify_results(result)
            except dynamo_resource.meta.client.exceptions.ResourceInUseException:
                self.fail()
            finally:
                table = await dynamo_resource.Table(self.table_name)
                await table.delete()

    async def __verify_results(self, result):
        results = result[0] + result[1]
        results.sort()
        self.assertEqual(len(results), 1000)
        for x in range(0, len(results) - 1):
            self.assertEqual(results[x] + 1, results[x + 1])

    async def __generate_large_number_of_ids(self, task, delay, db):
        ids = []
        for i in range(500):
            transaction_id = await db.next(self.key)
            ids.append(transaction_id)
            print(f'task:{task} - iteration:{i} - transaction_id:{transaction_id}')
            await asyncio.sleep(delay)
        return ids

    async def __create_table(self, dynamo_resource):
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
