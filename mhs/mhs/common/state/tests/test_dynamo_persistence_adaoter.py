import unittest
from unittest.mock import MagicMock, patch, Mock

from mhs.common.state import dynamo_persistence_adapter
from mhs.common.state.dynamo_persistence_adapter import DynamoPersistenceAdapter, RecordCreationError, \
    InvalidTableError, RecordRetrievalError, RecordDeletionError

TEST_STATE_ARN = "TEST STATE ARN"
TEST_ASYNC_ARN = "TEST ASYNC ARN"
TEST_ASYNC_TABLE = "TEST ASYNC TABLE"
TEST_STATE_TABLE = "TEST STATE TABLE"
TEST_INVALID_TABLE = "TEST INVALID TABLE"
TEST_DATA = "{\"test_attribute\": \"test_value\"}"
TEST_KEY = "TEST_KEY"
TEST_INVALID_KEY = "TEST INVALID KEY"
TEST_ITEM = {"key": TEST_KEY, "data": TEST_DATA}
TEST_GET_RESPONSE = {"Item": TEST_ITEM}
TEST_GET_EMPTY_RESPONSE = {}
TEST_DELETE_RESPONSE = {"Attributes": TEST_ITEM}
TEST_ADD_RESPONSE = {"Attributes": TEST_ITEM}
TEST_EXCEPTION = Exception()
TEST_SIDE_EFFECT = Mock(side_effect=TEST_EXCEPTION)


class TestDynamoPersistenceAdapter(unittest.TestCase):

    @patch.object(dynamo_persistence_adapter.boto3, "resource")
    def setUp(self, mock_boto3_resource):
        self.mock_dynamodb = MagicMock()
        mock_boto3_resource.return_value = self.mock_dynamodb

        self.mock_table = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table

        self.service = DynamoPersistenceAdapter(
            state_table=TEST_STATE_TABLE,
            state_arn=TEST_STATE_ARN,
            sync_async_table=TEST_ASYNC_TABLE,
            sync_async_arn=TEST_ASYNC_ARN
        )

    #   TESTING ADD METHOD
    def test_add_success_state(self):
        response = self.service.add(TEST_STATE_TABLE, TEST_KEY, TEST_ITEM)

        self.assertIsNone(response)

    def test_add_success_async(self):
        response = self.service.add(TEST_ASYNC_TABLE, TEST_KEY, TEST_ITEM)

        self.assertIsNone(response)

    def test_add_invalid_table(self):
        with self.assertRaises(RecordCreationError) as ex:
            self.service.add(TEST_INVALID_TABLE, TEST_KEY, TEST_ITEM)

        self.assertIsInstance(ex.exception.__cause__, InvalidTableError)

    def test_add_overwrite(self):
        self.mock_table.put_item.return_value = TEST_ADD_RESPONSE

        response = self.service.add(TEST_STATE_TABLE, TEST_KEY, TEST_ITEM)

        self.assertIsInstance(response, dict)

    def test_add_io_exception(self):
        self.mock_table.put_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(RecordCreationError) as ex:
            self.service.add(TEST_STATE_TABLE, TEST_KEY, TEST_ITEM)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)

    #   TESTING GET METHOD
    def test_get_success_state(self):
        self.mock_table.get_item.return_value = TEST_GET_RESPONSE

        response = self.service.get(TEST_STATE_TABLE, TEST_KEY)

        self.assertIsInstance(response, dict)

    def test_get_success_async(self):
        self.mock_table.get_item.return_value = TEST_GET_RESPONSE

        response = self.service.get(TEST_ASYNC_TABLE, TEST_KEY)

        self.assertIsInstance(response, dict)

    def test_get_invalid_table(self):
        with self.assertRaises(RecordRetrievalError) as ex:
            self.service.get(TEST_INVALID_TABLE, TEST_KEY)
        self.assertIsInstance(ex.exception.__cause__, InvalidTableError)

    def test_get_invalid_key(self):
        self.mock_table.get_item.return_value = TEST_GET_EMPTY_RESPONSE

        response = self.service.get(TEST_STATE_TABLE, TEST_INVALID_KEY)

        self.assertIsNone(response)

    def test_get_io_exception(self):
        self.mock_table.get_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(RecordRetrievalError) as ex:
            self.service.get(TEST_STATE_TABLE, TEST_INVALID_KEY)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)

    #   TESTING DELETE METHOD
    def test_delete_success_state(self):
        self.mock_table.delete_item.return_value = TEST_DELETE_RESPONSE

        response = self.service.delete(TEST_STATE_TABLE, TEST_KEY)

        self.assertIsInstance(response, dict)

    def test_delete_success_async(self):
        self.mock_table.delete_item.return_value = TEST_DELETE_RESPONSE

        response = self.service.delete(TEST_ASYNC_TABLE, TEST_KEY)

        self.assertIsInstance(response, dict)

    def test_delete_invalid_table(self):
        self.mock_table.delete_item.return_value = TEST_DELETE_RESPONSE

        with self.assertRaises(RecordDeletionError) as ex:
            self.service.delete(TEST_INVALID_TABLE, TEST_KEY)

        self.assertIsInstance(ex.exception.__cause__, InvalidTableError)

    def test_delete_invalid_key(self):
        self.mock_table.delete_item.return_value = TEST_GET_EMPTY_RESPONSE

        response = self.service.delete(TEST_STATE_TABLE, TEST_INVALID_KEY)

        self.assertIsNone(response)

    def test_delete_io_exception(self):
        self.mock_table.delete_item.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(RecordDeletionError) as ex:
            self.service.delete(TEST_STATE_TABLE, TEST_INVALID_KEY)

        self.assertIs(ex.exception.__cause__, TEST_EXCEPTION)
