"""
Provides a way of accessing a Dynamo table
"""
import os
import boto3


class DynamoWrapper(object):
    """
    Allows access to a DynamoDB instance
    """

    def __init__(self, table_name: str, **kwargs):
        """
        Initialise this instance with the dynamo connection configuration requited by boto3.
        :param kwargs: boto3 configuration arguments
        """
        self.dynamo_client = boto3.client('dynamodb', **kwargs)
        self.table_name = table_name

    def get_all_records_in_table(self) -> dict:
        """
        Returns all the records in the Dynamo instance within the given table name
        :param table: the table to retrieve records from
        :return: the records within the table
        """
        return self.dynamo_client.scan(TableName=self.table_name)

    def clear_all_records_in_table(self) -> None:
        """
        Deletes all records in the Dynamo instance within the given table name
        :param table: the table to delete all records from
        :return: None
        """
        scan = self.get_all_records_in_table()

        for each in scan['Items']:
            self.dynamo_client.delete_item(TableName=self.table_name, Key={'key': {'S': each['key']['S']}})


MHS_STATE_TABLE_DYNAMO_WRAPPER = DynamoWrapper \
    (table_name=os.environ.get('MHS_DYNAMODB_TABLE_NAME', 'mhs_state'),
     region_name='eu-west-2',
     endpoint_url=os.environ.get('MHS_DYNAMODB_ENDPOINT_URL', None))

MHS_SYNC_ASYNC_TABLE_DYNAMO_WRAPPER = DynamoWrapper(
    table_name=os.environ.get('MHS_SYNC_ASYNC_TABLE_NAME', 'sync_async_state'),
    region_name='eu-west-2',
    endpoint_url=os.environ.get('MHS_DYNAMODB_ENDPOINT_URL', None))
