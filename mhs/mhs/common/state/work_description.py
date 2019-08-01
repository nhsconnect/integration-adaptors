import enum
import json
import  utilities.integration_adaptors_logger as log


logger = log.IntegrationAdaptorsLogger('STATE_MANAGER')

class MessageStatus(enum.Enum):
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


class WorkDescription:

    def __init__(self, persistence_store, store_data: dict):
        if persistence_store is None:
            raise ValueError('Expected persistence store')
        
        self.persistence_store = persistence_store

        data = store_data['DATA']
        self.message_key = store_data[DATA_KEY]
        self.version = data[VERSION_KEY]
        self.timestamp = data[TIMESTAMP]
        self.status = data['STATUS']

    def publish(self):
        latest_data = self.persistence_store.get('default_table', self.message_key)
        if latest_data is not None:
            latest_version = latest_data[DATA][VERSION_KEY]
            if latest_version > self.version:
                raise OutOfDateVersionError(f'Failed to update message {self.message_key}: local version out of date ')

        serialised = self._serialise_data()

        old_data = self.persistence_store.add('default_table', serialised)
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
    def get_work_description_from_store(persistence_store, message_id):
        if persistence_store is None:
            raise ValueError('Expected non-null persistence store')
        if message_id is None:
            raise ValueError('Expected non-null message_id')
        json_store_data = persistence_store.get('default_table', message_id)
        return WorkDescription(persistence_store, json_store_data)

    @staticmethod
    def create_new_work_description(message_id: str,
                                    timestamp: str,
                                    status: MessageStatus):
        work_description_map = {
            DATA_KEY: message_id,
            "DATA": {
                TIMESTAMP: timestamp,
                'STATUS': status,
                VERSION_KEY: 1
            }
        }
        
        return WorkDescription(work_description_map)
        






