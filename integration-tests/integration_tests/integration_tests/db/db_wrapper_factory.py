import os

from integration_tests.db.dynamo_wrapper import DynamoWrapper
from integration_tests.db.mongo_wrapper import MongoWrapper

DYNAMODB_TYPE = "dynamodb"
MONGODB_TYPE = "mongodb"

DB_TYPE = os.environ.get('MHS_PERSISTENCE_ADAPTOR') or DYNAMODB_TYPE

DB_WRAPPER = {
    DYNAMODB_TYPE: DynamoWrapper,
    MONGODB_TYPE: MongoWrapper
}[DB_TYPE]

KEY_NAME = {
    DYNAMODB_TYPE: 'key',
    MONGODB_TYPE: '_id'
}[DB_TYPE]


MHS_STATE_TABLE_WRAPPER = DB_WRAPPER.get_state_table_wrapper()
MHS_SYNC_ASYNC_TABLE_WRAPPER = DB_WRAPPER.get_sync_async_table_wrapper()
