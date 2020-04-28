from __future__ import annotations

import enum
from typing import Optional

import utilities.integration_adaptors_logger as log
from utilities import timing

from retry import retriable_action
from persistence import persistence_adaptor as pa

logger = log.IntegrationAdaptorsLogger(__name__)


class MessageStatus(str, enum.Enum):
    OUTBOUND_MESSAGE_RECEIVED = 'OUTBOUND_MESSAGE_RECEIVED'
    OUTBOUND_MESSAGE_PREPARED = 'OUTBOUND_MESSAGE_PREPARED'
    OUTBOUND_MESSAGE_PREPARATION_FAILED = 'OUTBOUND_MESSAGE_PREPARATION_FAILED'
    OUTBOUND_MESSAGE_ACKD = 'OUTBOUND_MESSAGE_ACKD'
    OUTBOUND_MESSAGE_TRANSMISSION_FAILED = 'OUTBOUND_MESSAGE_TRANSMISSION_FAILED'
    OUTBOUND_MESSAGE_NACKD = 'OUTBOUND_MESSAGE_NACKD'

    OUTBOUND_SYNC_ASYNC_MESSAGE_LOADED = 'OUTBOUND_SYNC_ASYNC_MESSAGE_LOADED'
    OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND = 'OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND'
    OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED = 'OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED'

    OUTBOUND_MESSAGE_RESPONSE_RECEIVED = 'OUTBOUND_MESSAGE_RESPONSE_RECEIVED'

    INBOUND_RESPONSE_RECEIVED = 'INBOUND_RESPONSE_RECEIVED'
    INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED = 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED'
    INBOUND_RESPONSE_FAILED = 'INBOUND_RESPONSE_FAILED'

    UNSOLICITED_INBOUND_RESPONSE_RECEIVED = 'UNSOLICITED_INBOUND_RESPONSE_RECEIVED'
    UNSOLICITED_INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED = 'UNSOLICITED_INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED'
    UNSOLICITED_INBOUND_RESPONSE_FAILED = 'UNSOLICITED_INBOUND_RESPONSE_FAILED'

    INBOUND_SYNC_ASYNC_MESSAGE_STORED = 'INBOUND_SYNC_ASYNC_MESSAGE_STORED'
    INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED = 'INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED'

    SYNC_RESPONSE_SUCCESSFUL = "SYNC_RESPONSE_SUCCESSFUL"
    SYNC_RESPONSE_FAILED = "SYNC_RESPONSE_FAILED"


DATA_KEY = 'MESSAGE_KEY'
VERSION_KEY = 'VERSION'
CREATED_TIMESTAMP = 'CREATED'
LATEST_TIMESTAMP = 'LATEST_TIMESTAMP'
DATA = 'DATA'
INBOUND_STATUS = 'INBOUND_STATUS'
OUTBOUND_STATUS = 'OUTBOUND_STATUS'
WORKFLOW = 'WORKFLOW'


class OutOfDateVersionError(RuntimeError):
    """Exception thrown when trying to update a state and the local version is behind the remote version"""
    pass


class EmptyWorkDescriptionError(RuntimeError):
    """Exception thrown when no work description is found for a given key"""
    pass


class WorkDescriptionUpdateFailedError(RuntimeError):
    """Exception thrown when a work description could not be updated."""
    pass


async def update_status_with_retries(wdo: WorkDescription,
                                     update_status_method,
                                     status: MessageStatus,
                                     retries: int,
                                     retry_delay=0) -> None:
    """Update the status of the work description using the method provided. If the update fails, retries a configurable
    number of times.

    :param wdo: The work description object to be updated.
    :param update_status_method: The method to use to update the status.
    :param status: The new status to set.
    :param retries: The number of times to retry updating the work description if the first attempt fails.
    :param: retry_delay: The time (in seconds) to wait before retrying the update.
    :raises: OutOfDateVersionError if the local version of the work description is behind the remote version.
    :raises: WorkDescriptionUpdateFailedError if the work description could not be updated after retrying.
    """

    async def update_status():
        await wdo.update()
        await update_status_method(status)

    retry_result = await retriable_action.RetriableAction(update_status, retries, retry_delay) \
        .with_retriable_exception_check(lambda e: isinstance(e, OutOfDateVersionError)) \
        .execute()

    if not retry_result.is_successful:
        logger.error('Failed to update work description.')

        exception_raised = retry_result.exception
        if exception_raised:
            raise exception_raised

        raise WorkDescriptionUpdateFailedError


async def get_work_description_from_store(persistence_store: pa.PersistenceAdaptor, key: str) -> Optional[WorkDescription]:
    """
    Attempts to retrieve and deserialize a work description instance from the given persistence store to create
    a local work description
    :param persistence_store: persistence store to search for work description instance in
    :param key: key to look for
    :raise EmptyWorkDescriptionError: when no work description is found for the given key
    """

    if persistence_store is None:
        logger.error('Failed to get work description from store: persistence store is None')
        raise ValueError('Expected non-null persistence store')
    if key is None:
        logger.error('Failed to get work description from store: key is None')
        raise ValueError('Expected non-null key')

    json_store_data = await persistence_store.get(key)
    if json_store_data is None:
        logger.info('Persistence store returned empty value for {key}', fparams={'key': key})
        return None

    return WorkDescription(persistence_store, json_store_data)


def create_new_work_description(persistence_store: pa.PersistenceAdaptor,
                                key: str,
                                workflow: str,
                                inbound_status: Optional[MessageStatus] = None,
                                outbound_status: Optional[MessageStatus] = None
                                ) -> WorkDescription:
    """
    Builds a new local work description instance given the details of the message, these details are held locally
    until a `publish` is executed
    """
    if persistence_store is None:
        logger.error('Failed to build new work description, persistence store should not be null')
        raise ValueError('Expected persistence store to not be None')
    if not key:
        logger.error('Failed to build new work description, key should not be null or empty')
        raise ValueError('Expected key to not be None or empty')
    if workflow is None:
        logger.error('Failed to build new work description, workflow should not be null')
        raise ValueError('Expected workflow to not be None')
    if not inbound_status and not outbound_status:
        logger.error('Failed to build work description, expected inbound or outbound status to be present:'
                    '{inbound} {outbound}', fparams={'inbound': inbound_status, 'outbound': outbound_status})
        raise ValueError('Expected inbound/outbound to not be null')

    timestamp = timing.get_time()
    work_description_map = {
        DATA_KEY: key,
        DATA: {
            CREATED_TIMESTAMP: timestamp,
            LATEST_TIMESTAMP: timestamp,
            INBOUND_STATUS: inbound_status,
            OUTBOUND_STATUS: outbound_status,
            VERSION_KEY: 1,
            WORKFLOW: workflow
        }
    }

    return WorkDescription(persistence_store, work_description_map)


class WorkDescription(object):
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
        self._deserialize_data(store_data)

    async def publish(self):
        """
        Attempts to publish the local state of the work description to the state store, checks versions to avoid
        collisions
        :return:
        """
        logger.info('Attempting to publish work description {key}', fparams={'key': self.message_key})
        logger.info('Retrieving latest work description to check version')

        latest_data = await self.persistence_store.get(self.message_key)

        if latest_data is not None:
            logger.info('Retrieved previous version, comparing versions')
            latest_version = latest_data[DATA][VERSION_KEY]
            if latest_version == self.version:
                logger.info('Local version matches remote, incrementing local version number')
                self.version += 1
            elif latest_version > self.version:
                logger.error('Failed to update message {key}, local version out of date',
                             fparams={'key': self.message_key})
                raise OutOfDateVersionError(f'Failed to update message {self.message_key}: local version out of date')

        else:
            logger.info('No previous version found, continuing attempt to publish new version')
        self.last_modified_timestamp = timing.get_time()
        serialised = self._serialise_data()

        old_data = await self.persistence_store.add(self.message_key, serialised)
        logger.info('Successfully updated work description to state store for {key}',
                    fparams={'key': self.message_key})
        return old_data

    async def update(self):
        """
        This retrieves the remote version of the work description object and updates the local version
        :return:
        """
        json_store_data = await self.persistence_store.get(self.message_key)
        if json_store_data is None:
            logger.error('Persistence store returned empty value for {key}', fparams={'key': self.message_key})
            raise EmptyWorkDescriptionError(f'Failed to find a value for key id {self.message_key}')
        self._deserialize_data(json_store_data)

    async def set_inbound_status(self, new_status: MessageStatus):
        """
        Helper method for setting the status and publishing to the state store

        :param new_status: new status to set
        """
        self.inbound_status = new_status
        await self.publish()

    async def set_outbound_status(self, new_status: MessageStatus):
        """
        Helper method for setting the status and publishing to the state store

        :param new_status: new status to set
        """
        self.outbound_status = new_status
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
                INBOUND_STATUS: self.inbound_status,
                OUTBOUND_STATUS: self.outbound_status,
                WORKFLOW: self.workflow
            }
        }

    def _deserialize_data(self, store_data):
        data_attribute = store_data[DATA]
        self.message_key: str = store_data.get(DATA_KEY)
        self.version: int = data_attribute.get(VERSION_KEY)
        self.created_timestamp: str = data_attribute.get(CREATED_TIMESTAMP)
        self.last_modified_timestamp: str = data_attribute.get(LATEST_TIMESTAMP)
        self.inbound_status: MessageStatus = data_attribute.get(INBOUND_STATUS)
        self.outbound_status: MessageStatus = data_attribute.get(OUTBOUND_STATUS)
        self.workflow: str = data_attribute.get(WORKFLOW)
