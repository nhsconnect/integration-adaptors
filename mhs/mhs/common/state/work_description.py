import json
import utilities.integration_adaptors_logger as log


logger = log.IntegrationAdaptorsLogger('STATE_MANAGER')


class MessageStatus:
    RECEIVED = 1
    STARTED = 2
    IN_OUTBOUND_WORKFLOW = 3


DATA_KEY = 'MESSAGE_KEY'
VERSION_KEY = 'VERSION'
TIMESTAMP = 'TIMESTAMP'
DATA = 'DATA'
STATUS = 'STATUS'


class OutOfDateVersionError(RuntimeError):
    pass


class EmptyWorkDescription(RuntimeError):
    pass


class WorkDescription:

    def __init__(self, persistence_store, table_name: str, store_data: dict):
        if persistence_store is None:
            raise ValueError('Expected persistence store')
        if not table_name:
            raise ValueError('Expected non empty table name')

        self.persistence_store = persistence_store
        self.table_name = table_name

        data = store_data[DATA]
        self.message_key = store_data[DATA_KEY]
        self.version = data[VERSION_KEY]
        self.timestamp = data[TIMESTAMP]
        self.status = data[STATUS]

    def publish(self):
        latest_data = self.persistence_store.get(self.table_name, self.message_key)
        if latest_data is not None:
            latest_version = latest_data[DATA][VERSION_KEY]
            if latest_version > self.version:
                raise OutOfDateVersionError(f'Failed to update message {self.message_key}: local version out of date ')

        serialised = self._serialise_data()

        old_data = self.persistence_store.add(self.table_name, serialised)
        return old_data

    def _serialise_data(self):
        data = {
            DATA_KEY: self.message_key,
            'DATA': {
                TIMESTAMP: self.timestamp,
                VERSION_KEY: self.version,
                STATUS: self.status
            }
        }

        return json.dumps(data)


class WorkDescriptionFactory:

    @staticmethod
    def get_work_description_from_store(persistence_store, table_name: str, key: str):
        if persistence_store is None:
            logger.error('001', 'Failed to get work description from store: persistence store is None')
            raise ValueError('Expected non-null persistence store')
        if key is None:
            logger.error('002', 'Failed to get work description from store: key is None')
            raise ValueError('Expected non-null key')

        json_store_data = persistence_store.get(table_name, key)
        if json_store_data is None:
            logger.error('003', 'Persistence store returned empty value for {key}', {'key': key})
            raise EmptyWorkDescription(f'Failed to find a value for key id {key}')

        return WorkDescription(persistence_store, table_name, json_store_data)

    @staticmethod
    def create_new_work_description(persistence_store,
                                    table_name: str,
                                    key: str,
                                    timestamp: str,
                                    status: MessageStatus):
        if persistence_store is None:
            logger.error('004', 'Failed to build new work description, persistence store should not be null')
            raise ValueError('Expected persistence store to not be None')
        if not key:
            logger.error('005', 'Failed to build new work description, key should not be null or empty')
            raise ValueError('Expected key to not be None or empty')
        if timestamp is None:
            logger.error('006', 'Failed to build new work description, timestamp should not be null')
            raise ValueError('Expected timestamp to not be None')
        if status is None:
            logger.error('007', 'Failed to build new work description, status should not be null')
            raise ValueError('Expected status to not be None')

        work_description_map = {
            DATA_KEY: key,
            DATA: {
                TIMESTAMP: timestamp,
                STATUS: status,
                VERSION_KEY: 1
            }
        }
        
        return WorkDescription(persistence_store, table_name, work_description_map)
        






