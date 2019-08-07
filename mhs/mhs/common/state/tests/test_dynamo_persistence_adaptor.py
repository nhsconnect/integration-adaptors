"""Module to test dynamo persistence adaptor functionality."""
import asyncio
import contextlib
import json
import unittest
from unittest.mock import patch, Mock, MagicMock

from utilities.test_utilities import async_test

from mhs.common.state import dynamo_persistence_adaptor
from mhs.common.state.dynamo_persistence_adaptor import DynamoPersistenceAdaptor, RecordCreationError, \
    RecordRetrievalError, RecordDeletionError

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
TEST_SIDE_EFFECT = Mock(side_effect=TEST_EXCEPTION)


class TestDynamoPersistenceAdaptor(unittest.TestCase):
    """Unit tests for the DynamoPersistenceAdaptor"""

    def setUp(self):
        """Configure a dynamo persistence adaptor with the boto3 calls mocked."""

        self.service = DynamoPersistenceAdaptor(
            table_name=TEST_TABLE_ARN
        )

    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_add_success(self, mock_boto3_resource):
        """Test happy path for add call with no previous object."""
        self.__configure_mocks(mock_boto3_resource)
        self.__setFutureResponse(self.mock_table.put_item, TEST_ADD_EMPTY_RESPONSE)

        response = await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        self.assertIsNone(response)

    #   TESTING ADD METHOD

    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_add_overwrite(self, mock_boto3_resource):
        """Test happy path for add call, overwriting existing object."""
        self.__configure_mocks(mock_boto3_resource)
        self.__setFutureResponse(self.mock_table.put_item, TEST_ADD_RESPONSE)

        response = await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        self.assertEqual(response, TEST_DATA_OBJECT)

    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_add_io_exception(self, mock_boto3_resource):
        """Test unhappy path for add where an IO exception occurs."""
        self.__configure_mocks(mock_boto3_resource)
        self.mock_table.put_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(RecordCreationError) as ex:
            await self.service.add(TEST_KEY, TEST_DATA_OBJECT)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)

    #   TESTING GET METHOD
    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_get_success(self, mock_boto3_resource):
        """Test happy path for get."""
        self.__configure_mocks(mock_boto3_resource)
        self.__setFutureResponse(self.mock_table.get_item, TEST_GET_RESPONSE)

        response = await self.service.get(TEST_KEY)

        self.assertEqual(response, TEST_DATA_OBJECT)

    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_get_invalid_key(self, mock_boto3_resource):
        """Test unhappy path for get where an invalid/missing key is provided."""
        self.__configure_mocks(mock_boto3_resource)
        self.__setFutureResponse(self.mock_table.get_item, TEST_GET_EMPTY_RESPONSE)

        response = await self.service.get(TEST_INVALID_KEY)

        self.assertIsNone(response)

    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_get_io_exception(self, mock_boto3_resource):
        """Test unhappy path for get where an IO exception occurs."""
        self.__configure_mocks(mock_boto3_resource)
        self.mock_table.get_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(RecordRetrievalError) as ex:
            await self.service.get(TEST_INVALID_KEY)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)

    #   TESTING DELETE METHOD
    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_delete_success(self, mock_boto3_resource):
        """Test happy path for delete."""
        self.__configure_mocks(mock_boto3_resource)
        self.__setFutureResponse(self.mock_table.delete_item, TEST_DELETE_RESPONSE)

        response = await self.service.delete(TEST_KEY)

        self.assertEqual(response, TEST_DATA_OBJECT)

    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_delete_invalid_key(self, mock_boto3_resource):
        """Test unhappy path for delete where a invalid/missing key is provided."""
        self.__configure_mocks(mock_boto3_resource)
        self.__setFutureResponse(self.mock_table.delete_item, TEST_DELETE_EMPTY_RESPONSE)

        response = await self.service.delete(TEST_INVALID_KEY)

        self.assertIsNone(response)

    @patch.object(dynamo_persistence_adaptor.aioboto3, "resource")
    @async_test
    async def test_delete_io_exception(self, mock_boto3_resource):
        """Test unhappy path for delete where an IO exception occurs."""
        self.__configure_mocks(mock_boto3_resource)
        self.mock_table.delete_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(RecordDeletionError) as ex:
            await self.service.delete(TEST_INVALID_KEY)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)

    @staticmethod
    def __setFutureResponse(method, response) -> None:
        """
        Utility method to help setting expected responses on an async/await call.
        :param method: The method to add the response to.
        :param response: The response to be added to the method.
        """
        future = asyncio.Future()
        future.set_result(response)

        method.return_value = future

    def __configure_mocks(self, mock_boto3_resource):
        """Configure the standard mocks to have mappings which can be used in the tests."""
        mock = MagicMock()
        self.mock_table = mock.Table.return_value
        mock_boto3_resource.return_value = constant_context_manager(mock)


@contextlib.asynccontextmanager
async def constant_context_manager(mock: Mock):
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

    def wrapper(*args, **kwargs):
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
        self.service = DynamoPersistenceAdaptor(
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
