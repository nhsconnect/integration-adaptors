import os

import boto3


class DynamoWrapper(object):
    """
    Allows access to a DynamoDB instance
    """

    def __init__(self, **kwargs):
        """
        Initialise this instance with the dynamo connection configuration requited by boto3.
        :param kwargs: boto3 configuration arguments
        """
        self.dynamo_client = boto3.client('dynamodb', **kwargs)

    def get_all_records_in_table(self, table: str):
        """
        Returns all the records in the Dynamo instance within the given table name
        :param table: the table to retrieve records from
        :return: the records within the table
        """
        return self.dynamo_client.scan(TableName=table)

    def clear_all_records_in_table(self, table: str):
        """
        Deletes all records in the Dynamo instance within the given table name
        :param table: the table to delete all records from
        :return: None
        """
        scan = self.get_all_records_in_table(table)

        for each in scan['Items']:
            self.dynamo_client.delete_item(TableName=table, Key={'key': {'S': each['key']['S']}})


DYNAMO_WRAPPER = DynamoWrapper(
    region_name=os.environ.get('DYNAMO_DB_REGION', 'eu-west-2'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY', 'anything'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY', 'anything'),
    endpoint_url=os.environ.get('DYNAMO_ENDPOINT_URL', 'http://localhost:8000'))
