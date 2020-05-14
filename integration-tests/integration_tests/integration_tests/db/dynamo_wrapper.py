"""
Provides a way of accessing a Dynamo table
"""
import os

import boto3

from integration_tests.db.db_wrapper import DbWrapper


class DynamoWrapper(DbWrapper):
    """
    Allows access to a DynamoDB instance
    """

    def __init__(self, table_name: str, region_name: str, endpoint_url: str):
        """
        Initialise this instance with the dynamo connection configuration requited by boto3.
        :param kwargs: boto3 configuration arguments
        """
        self.table_name = table_name
        dynamo_resource = boto3.resource('dynamodb', region_name=region_name, endpoint_url=endpoint_url)
        self.table = dynamo_resource.Table(self.table_name)

    def get_all_records_in_table(self) -> list:
        """
        Returns all the records in the Dynamo instance within the given table name
        :return: the records within the table
        """
        return self.table.scan()['Items']

    def clear_all_records_in_table(self) -> None:
        """
        Deletes all records in the Dynamo instance within the given table name
        :param table: the table to delete all records from
        :return: None
        """
        records = self.get_all_records_in_table()

        for each in records:
            self.table.delete_item(Key={'key': each['key']})

    @staticmethod
    def get_state_table_wrapper():
        return DynamoWrapper(
            table_name=os.environ.get('MHS_STATE_TABLE_NAME', 'mhs_state'),
            region_name=os.environ.get('MHS_CLOUD_REGION', 'eu-west-2'),
            endpoint_url=os.environ.get('MHS_DB_ENDPOINT_URL', None))

    @staticmethod
    def get_sync_async_table_wrapper():
        return DynamoWrapper(
            table_name=os.environ.get('MHS_SYNC_ASYNC_TABLE_NAME', 'sync_async_state'),
            region_name=os.environ.get('MHS_CLOUD_REGION', 'eu-west-2'),
            endpoint_url=os.environ.get('MHS_DB_ENDPOINT_URL', None))
