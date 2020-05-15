"""
Provides a way of accessing a MongoDB collection
"""
import os

from pymongo import MongoClient

from integration_tests.db.db_wrapper import DbWrapper

_DB_NAME = 'integration-adaptors'


class MongoWrapper(DbWrapper):
    """
    Allows access to a MongoDB instance
    """

    def __init__(self, table_name: str, endpoint_url: str):
        """
        Initialise this instance with the dynamo connection configuration requited by boto3.
        """
        self.collection = MongoClient(endpoint_url)[_DB_NAME][table_name]

    def get_all_records_in_table(self) -> list:
        """
        Returns all the records in the Mongo instance within the given table name
        :return: the records within the collection
        """
        return list(self.collection.find({}))

    def clear_all_records_in_table(self) -> None:
        """
        Deletes all records in the MongoDB instance within the given collection
        :return: None
        """
        result = self.collection.delete_many({})
        if not result.acknowledged:
            raise RuntimeError

    @staticmethod
    def get_state_table_wrapper():
        return MongoWrapper(
            table_name=os.environ.get('MHS_STATE_TABLE_NAME', 'mhs_state'),
            endpoint_url=os.environ.get('MHS_DB_ENDPOINT_URL', None))

    @staticmethod
    def get_sync_async_table_wrapper():
        return MongoWrapper(
            table_name=os.environ.get('MHS_SYNC_ASYNC_TABLE_NAME', 'sync_async_state'),
            endpoint_url=os.environ.get('MHS_DB_ENDPOINT_URL', None))
