import os

from integration_tests.db.dynamo_wrapper import DynamoWrapper
from integration_tests.db.mongo_wrapper import MongoWrapper

_STATE_TABLE_WRAPPER_FACTORY = {
    'dynamodb': DynamoWrapper.get_state_table_wrapper,
    'mongodb': MongoWrapper.get_state_table_wrapper
}
_SYNC_ASYNC_TABLE_WRAPPER_FACTORY = {
    'dynamodb': DynamoWrapper.get_sync_async_table_wrapper,
    'mongodb': MongoWrapper.get_sync_async_table_wrapper
}

DB_TYPE = os.environ.get('MHS_PERSISTENCE_ADAPTOR')
KEY_NAME = {
    'dynamodb': 'key',
    'mongodb': '_id'
}[DB_TYPE]


MHS_STATE_TABLE_WRAPPER = _STATE_TABLE_WRAPPER_FACTORY[DB_TYPE]()
MHS_SYNC_ASYNC_TABLE_WRAPPER = _SYNC_ASYNC_TABLE_WRAPPER_FACTORY[DB_TYPE]()
