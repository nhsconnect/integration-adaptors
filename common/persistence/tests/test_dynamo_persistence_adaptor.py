"""Module to test dynamo persistence adaptor functionality."""
import asyncio
import contextlib
import functools
import json
import unittest.mock

import utilities.config
from utilities import test_utilities

import persistence.dynamo_persistence_adaptor

TEST_TABLE_ARN = "TEST TABLE ARN"
TEST_DATA_OBJECT = {"test_attribute": "test_value"}
TEST_DATA = json.dumps(TEST_DATA_OBJECT)
TEST_KEY = "TEST_KEY"
TEST_INVALID_KEY = "TEST INVALID KEY"
TEST_ITEM = {"key": TEST_KEY, "data": TEST_DATA}
TEST_GET_RESPONSE = {"Item": TEST_ITEM}
TEST_GET_EMPTY_RESPONSE = {}
TEST_DELETE_RESPONSE = {"Attributes": TEST_ITEM}
TEST_DELETE_EMPTY_RESPONSE = {}
TEST_ADD_EMPTY_RESPONSE = {"Attributes": {}}
TEST_ADD_RESPONSE = {"Attributes": TEST_ITEM}
TEST_EXCEPTION = Exception()
TEST_SIDE_EFFECT = unittest.mock.Mock(side_effect=TEST_EXCEPTION)


class TestDynamoPersistenceAdaptor(unittest.TestCase):
    """Unit tests for the DynamoPersistenceAdaptor"""

    def setUp(self):
        """Configure a dynamo persistence adaptor with the boto3 calls mocked."""
        patcher = unittest.mock.patch.object(persistence.dynamo_persistence_adaptor.aioboto3, "resource")
        self.mock_boto3_resource = patcher.start()
        self.addCleanup(patcher.stop)
        self.__configure_mocks(self.mock_boto3_resource)
        self.service = persistence.dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
            table_name=TEST_TABLE_ARN
        )

    #   TESTING ADD METHOD
    @test_utilities.async_test
    async def test_add_success(self):
        """Test happy path for add call with no previous object."""
        self.__setFutureResponse(self.mock_table.put_item, TEST_ADD_EMPTY_RESPONSE)

        response = await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        self.assertIsNone(response)

    @test_utilities.async_test
    async def test_add_overwrite(self):
        """Test happy path for add call, overwriting existing object."""
        self.__setFutureResponse(self.mock_table.put_item, TEST_ADD_RESPONSE)

        response = await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        self.assertEqual(response, TEST_DATA_OBJECT)

    @test_utilities.async_test
    async def test_add_io_exception(self):
        """Test unhappy path for add where an IO exception occurs."""
        self.mock_table.put_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(persistence.dynamo_persistence_adaptor.RecordCreationError) as ex:
            await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)

    #   TESTING GET METHOD
    @test_utilities.async_test
    async def test_get_success(self):
        """Test happy path for get."""
        self.__setFutureResponse(self.mock_table.get_item, TEST_GET_RESPONSE)

        response = await self.service.get(TEST_KEY)

        self.assertEqual(response, TEST_DATA_OBJECT)

    @test_utilities.async_test
    async def test_get_invalid_key(self):
        """Test unhappy path for get where an invalid/missing key is provided."""
        self.__setFutureResponse(self.mock_table.get_item, TEST_GET_EMPTY_RESPONSE)

        response = await self.service.get(TEST_INVALID_KEY)

        self.assertIsNone(response)

    @test_utilities.async_test
    async def test_get_io_exception(self):
        """Test unhappy path for get where an IO exception occurs."""
        self.mock_table.get_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(persistence.dynamo_persistence_adaptor.RecordRetrievalError) as ex:
            await self.service.get(TEST_INVALID_KEY)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)

    #   TESTING DELETE METHOD
    @test_utilities.async_test
    async def test_delete_success(self):
        """Test happy path for delete."""
        self.__setFutureResponse(self.mock_table.delete_item, TEST_DELETE_RESPONSE)

        response = await self.service.delete(TEST_KEY)

        self.assertEqual(response, TEST_DATA_OBJECT)

    @test_utilities.async_test
    async def test_delete_invalid_key(self):
        """Test unhappy path for delete where a invalid/missing key is provided."""
        self.__setFutureResponse(self.mock_table.delete_item, TEST_DELETE_EMPTY_RESPONSE)

        response = await self.service.delete(TEST_INVALID_KEY)

        self.assertIsNone(response)

    @test_utilities.async_test
    async def test_delete_io_exception(self):
        """Test unhappy path for delete where an IO exception occurs."""
        self.mock_table.delete_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(persistence.dynamo_persistence_adaptor.RecordDeletionError) as ex:
            await self.service.delete(TEST_INVALID_KEY)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)

    #   TESTING BOTO3 RESOURCE CALL
    @test_utilities.async_test
    async def test_boto3_resource_created_correctly(self):
        self.__setFutureResponse(self.mock_table.get_item, TEST_GET_RESPONSE)

        await self.service.get(TEST_KEY)

        self.mock_boto3_resource.assert_called_once_with('dynamodb', region_name='eu-west-2', endpoint_url=None)

    @unittest.mock.patch.dict(utilities.config.config, {'DYNAMODB_ENDPOINT_URL': 'http://localhost:8000'})
    @test_utilities.async_test
    async def test_boto3_resource_created_correctly_with_endpoint_url(self):
        self.__setFutureResponse(self.mock_table.get_item, TEST_GET_RESPONSE)

        await self.service.get(TEST_KEY)

        self.mock_boto3_resource.assert_called_once_with('dynamodb', region_name='eu-west-2',
                                                         endpoint_url='http://localhost:8000')

    @staticmethod
    def __setFutureResponse(method, response) -> None:
        """
        Utility method to help setting expected responses on an async/await call.
        :param method: The method to add the response to.
        :param response: The response to be added to the method.
        """
        method.return_value = test_utilities.awaitable(response)

    def __configure_mocks(self, mock_boto3_resource):
        """Configure the standard mocks to have mappings which can be used in the tests."""
        mock = unittest.mock.MagicMock()
        self.mock_table = mock.Table.return_value
        mock_boto3_resource.return_value = constant_context_manager(mock)


@contextlib.asynccontextmanager
async def constant_context_manager(mock: unittest.mock.Mock):
    """
    Create a context manager which will provide a mock.
    :param mock: The mock to provide.
    :return: The mock required.
    """
    yield mock


def single_loop_async_test(f):
    """
    A wrapper for asynchronous tests.
    By default unittest will not wait for asynchronous tests to complete even if the async functions are awaited.
    By annotating a test method with `@async_test` it will cause the test to wait for asynchronous activities
    to complete. This will only use a single event loop for all tests with this annotation.
    :param f: The coroutine which will be executed.
    :return: a function which will execute an asynchronous unit test.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        """
        The wrapper function which will execute the provided coroutine within the shared event loop until it has
        completed.
        :param args: Arguments passed into the coroutine.
        :param kwargs: Key word arguments passed into the coroutine.
        :return: Only once the coroutine has completed.
        """
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


@unittest.skip("This has been configured for a specific test dynamo instance which may not exist.")
class ComponentTestDynamoPersistenceAdaptor(unittest.TestCase):
    """Component tests for a DynamoDB persistence adaptor."""

    def setUp(self):
        """Configure a dynamo persistence adaptor with active boto3 calls."""
        self.service = persistence.dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
            table_name="custom_test_db"
        )

    #   TESTING ADD METHOD
    @single_loop_async_test
    async def test_add_success(self):
        """Test happy path for add call with no previous object."""
        response = await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        self.assertIsNone(response)

        await self.service.delete(TEST_KEY)

    #   TESTING GET METHOD
    @single_loop_async_test
    async def test_get_success(self):
        """Test happy path for get."""
        await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        response = await self.service.get(TEST_KEY)

        self.assertEqual(TEST_DATA_OBJECT, response)

        await self.service.delete(TEST_KEY)

    #   TESTING DELETE METHOD
    @single_loop_async_test
    async def test_delete_success(self):
        """Test happy path for delete."""
        await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        response = await self.service.delete(TEST_KEY)
        self.assertEqual(TEST_DATA_OBJECT, response)
