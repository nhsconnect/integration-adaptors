from __future__ import annotations
import json
import utilities.integration_adaptors_logger as log
import datetime

from utilities import timing

from mhs_common.state import persistence_adaptor as pa
import enum

logger = log.IntegrationAdaptorsLogger('STATE_MANAGER')


class MessageStatus(str, enum.Enum):
    OUTBOUND_MESSAGE_RECEIVED = 'OUTBOUND_MESSAGE_RECEIVED'
    OUTBOUND_MESSAGE_PREPARED = 'OUTBOUND_MESSAGE_PREPARED'
    OUTBOUND_MESSAGE_PREPARATION_FAILED = 'OUTBOUND_MESSAGE_PREPARATION_FAILED'
    OUTBOUND_MESSAGE_ACKD = 'OUTBOUND_MESSAGE_ACKD'
    OUTBOUND_MESSAGE_TRANSMISSION_FAILED = 'OUTBOUND_MESSAGE_TRANSMISSION_FAILED'
    OUTBOUND_MESSAGE_NACKD = 'OUTBOUND_MESSAGE_NACKD'
    INBOUND_RESPONSE_RECEIVED = 'INBOUND_RESPONSE_RECEIVED'
    INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED = 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED'
    INBOUND_RESPONSE_FAILED = 'INBOUND_RESPONSE_FAILED'
    INBOUND_SYNC_ASYNC_MESSAGE_STORED = 'INBOUND_SYNC_ASYNC_MESSAGE_STORED'
    INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED = 'INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED'
    


DATA_KEY = 'MESSAGE_KEY'
VERSION_KEY = 'VERSION'
CREATED_TIMESTAMP = 'CREATED'
LATEST_TIMESTAMP = 'LATEST_TIMESTAMP'
DATA = 'DATA'
STATUS = 'STATUS'
WORKFLOW = 'WORKFLOW'


class OutOfDateVersionError(RuntimeError):
    """Exception thrown when trying to update a state and the local version is behind the remote version"""
    pass


class EmptyWorkDescriptionError(RuntimeError):
    """Exception thrown when no work description is found for a given key"""
    pass


async def get_work_description_from_store(persistence_store: pa.PersistenceAdaptor, key: str) -> WorkDescription:
    """
    Attempts to retrieve and deserialize a work description instance from the given persistence store to create
    a local work description
    """

    if persistence_store is None:
        logger.error('001', 'Failed to get work description from store: persistence store is None')
        raise ValueError('Expected non-null persistence store')
    if key is None:
        logger.error('002', 'Failed to get work description from store: key is None')
        raise ValueError('Expected non-null key')

    json_store_data = await persistence_store.get(key)
    if json_store_data is None:
        logger.error('003', 'Persistence store returned empty value for {key}', {'key': key})
        raise EmptyWorkDescriptionError(f'Failed to find a value for key id {key}')

    return WorkDescription(persistence_store, json_store_data)


def create_new_work_description(persistence_store: pa.PersistenceAdaptor,
                                key: str,
                                status: MessageStatus,
                                workflow: str
                                ) -> WorkDescription:
    """
    Builds a new local work description instance given the details of the message, these details are held locally
    until a `publish` is executed
    """
    if persistence_store is None:
        logger.error('004', 'Failed to build new work description, persistence store should not be null')
        raise ValueError('Expected persistence store to not be None')
    if not key:
        logger.error('005', 'Failed to build new work description, key should not be null or empty')
        raise ValueError('Expected key to not be None or empty')
    if status is None:
        logger.error('007', 'Failed to build new work description, status should not be null')
        raise ValueError('Expected status to not be None')
    if workflow is None:
        logger.error('008', 'Failed to build new work description, workflow should not be null')
        raise ValueError('Expected workflow to not be None')

    timestamp = timing.get_time()
    work_description_map = {
        DATA_KEY: key,
        DATA: {
            CREATED_TIMESTAMP: timestamp,
            LATEST_TIMESTAMP: timestamp,
            STATUS: status,
            VERSION_KEY: 1,
            WORKFLOW: workflow
        }
    }

    return WorkDescription(persistence_store, work_description_map)


class WorkDescription:
    """A local copy of an instance of a work description from the state store"""

    def __init__(self, persistence_store: pa.PersistenceAdaptor, store_data: dict):
        """
        Given 
        :param persistence_store:
        :param store_data:
        """
        if persistence_store is None:
            raise ValueError('Expected persistence store')

        self.persistence_store = persistence_store

        data = store_data[DATA]
        self.message_key: str = store_data[DATA_KEY]
        self.version: int = data[VERSION_KEY]
        self.created_timestamp: str = data[CREATED_TIMESTAMP]
        self.last_modified_timestamp: str = data[LATEST_TIMESTAMP]
        self.status: MessageStatus = data[STATUS]
        self.workflow: str = data[WORKFLOW]

    async def publish(self):
        """
        Attempts to publish the local state of the work description to the state store, checks versions to avoid
        collisions
        :return:
        """
        logger.info('011', 'Attempting to publish work description {key}', {'key': self.message_key})
        logger.info('012', 'Retrieving latest work description to check version')

        latest_data = await self.persistence_store.get(self.message_key)
        if latest_data is not None:
            logger.info('013', 'Retrieved previous version, comparing versions')
            latest_version = latest_data[DATA][VERSION_KEY]
            if latest_version == self.version:
                logger.info('017', 'Local version matches remote, incrementing local version number')
                self.version += 1
            elif latest_version > self.version:
                logger.error('014', 'Failed to update message {key}, local version out of date',
                             {'key': self.message_key})
                raise OutOfDateVersionError(f'Failed to update message {self.message_key}: local version out of date')

        else:
            logger.info('015', 'No previous version found, continuing attempt to publish new version')
        self.last_modified_timestamp = timing.get_time()
        serialised = self._serialise_data()

        old_data = await self.persistence_store.add(self.message_key, serialised)
        logger.info('016', 'Successfully updated work description to state store for {key}', {'key': self.message_key})
        return old_data

    async def set_status(self, new_status: MessageStatus):
        """
        Helper method for setting the status and publishing to the state store

        :param new_status: new status to set
        """
        self.status = new_status
        await self.publish()

    def _serialise_data(self):
        """
        A simple serialization method that produces an object from the local data which can be stored in the
        persistence store
        """
        return {
            DATA_KEY: self.message_key,
            DATA: {
                CREATED_TIMESTAMP: self.created_timestamp,
                LATEST_TIMESTAMP: self.last_modified_timestamp,
                VERSION_KEY: self.version,
                STATUS: self.status,
                WORKFLOW: self.workflow
            }
        }
