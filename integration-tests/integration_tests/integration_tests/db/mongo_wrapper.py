"""
Provides a way of accessing a Dynamo table
"""
import os

from pymongo import MongoClient

_DB_NAME = 'integration-adaptors'


class MongoWrapper:
    """
    Allows access to a DynamoDB instance
    """

    def __init__(self, table_name: str, endpoint_url: str):
        """
        Initialise this instance with the dynamo connection configuration requited by boto3.
        :param kwargs: boto3 configuration arguments
        """
        self.collection = MongoClient(endpoint_url)[_DB_NAME][table_name]

    def get_all_records_in_table(self) -> list:
        """
        Returns all the records in the Mongo instance within the given table name
        :return: the records within the table
        """
        return list(self.collection.find({}))

    def clear_all_records_in_table(self) -> None:
        """
        Deletes all records in the Dynamo instance within the given table name
        :param table: the table to delete all records from
        :return: None
        """
        result = self.collection.delete_many({})
        if not result.acknowledged:
            raise RuntimeError

    @staticmethod
    def get_state_table_wrapper():
        return MongoWrapper(
            table_name=os.environ.get('MHS_DYNAMODB_TABLE_NAME', 'mhs_state'),
            endpoint_url=os.environ.get('MHS_MONGODB_ENDPOINT_URL', None))

    @staticmethod
    def get_sync_async_table_wrapper():
        return MongoWrapper(
            table_name=os.environ.get('MHS_SYNC_ASYNC_TABLE_NAME', 'sync_async_state'),
            endpoint_url=os.environ.get('MHS_MONGODB_ENDPOINT_URL', None))
