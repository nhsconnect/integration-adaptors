from __future__ import annotations

import enum
from typing import Optional

import utilities.integration_adaptors_logger as log
from persistence import persistence_adaptor as pa
from utilities import timing

logger = log.IntegrationAdaptorsLogger(__name__)


class MessageStatus(str, enum.Enum):
    OUTBOUND_MESSAGE_RECEIVED = 'OUTBOUND_MESSAGE_RECEIVED'
    OUTBOUND_MESSAGE_PREPARATION_FAILED = 'OUTBOUND_MESSAGE_PREPARATION_FAILED'
    OUTBOUND_MESSAGE_ACKD = 'OUTBOUND_MESSAGE_ACKD'
    OUTBOUND_MESSAGE_TRANSMISSION_FAILED = 'OUTBOUND_MESSAGE_TRANSMISSION_FAILED'
    OUTBOUND_MESSAGE_NACKD = 'OUTBOUND_MESSAGE_NACKD'

    OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND = 'OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND'
    OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED = 'OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED'

    OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED = 'OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED'

    INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED = 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED'
    INBOUND_RESPONSE_FAILED = 'INBOUND_RESPONSE_FAILED'

    UNSOLICITED_INBOUND_RESPONSE_RECEIVED = 'UNSOLICITED_INBOUND_RESPONSE_RECEIVED'
    UNSOLICITED_INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED = 'UNSOLICITED_INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED'
    UNSOLICITED_INBOUND_RESPONSE_FAILED = 'UNSOLICITED_INBOUND_RESPONSE_FAILED'

    INBOUND_SYNC_ASYNC_MESSAGE_STORED = 'INBOUND_SYNC_ASYNC_MESSAGE_STORED'
    INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED = 'INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED'

    SYNC_RESPONSE_SUCCESSFUL = "SYNC_RESPONSE_SUCCESSFUL"
    SYNC_RESPONSE_FAILED = "SYNC_RESPONSE_FAILED"


MESSAGE_ID = 'MESSAGE_ID'
CREATED_TIMESTAMP = 'CREATED'
INBOUND_STATUS = 'INBOUND_STATUS'
OUTBOUND_STATUS = 'OUTBOUND_STATUS'
WORKFLOW = 'WORKFLOW'


class OutOfDateVersionError(RuntimeError):
    """Exception thrown when trying to update a state and the local version is behind the remote version"""
    pass


class EmptyWorkDescriptionError(RuntimeError):
    """Exception thrown when no work description is found for a given message_id"""
    pass


class WorkDescriptionUpdateFailedError(RuntimeError):
    """Exception thrown when a work description could not be updated."""
    pass


async def get_work_description_from_store(persistence_store: pa.PersistenceAdaptor, message_id: str) -> Optional[WorkDescription]:
    """
    Attempts to retrieve and deserialize a work description instance from the given persistence store to create
    a local work description
    :param persistence_store: persistence store to search for work description instance in
    :param message_id: message_id to look for
    :raise EmptyWorkDescriptionError: when no work description is found for the given message_id
    """

    if persistence_store is None:
        logger.error('Failed to get work description from store: persistence store is None')
        raise ValueError('Expected non-null persistence store')
    if message_id is None:
        logger.error('Failed to get work description from store: message_id is None')
        raise ValueError('Expected non-null message_id')

    json_store_data = await persistence_store.get(message_id, strongly_consistent_read=True)
    if json_store_data is None:
        logger.info('Persistence store returned empty value for {message_id}', fparams={'message_id': message_id})
        return None

    return WorkDescription(persistence_store, json_store_data)


def build_store_data(message_id: str,
                     created_at: str,
                     workflow: str,
                     inbound_status: Optional[str] = None,
                     outbound_status: Optional[str] = None) -> dict:
    return {
        MESSAGE_ID: message_id,
        CREATED_TIMESTAMP: created_at,
        INBOUND_STATUS: inbound_status,
        OUTBOUND_STATUS: outbound_status,
        WORKFLOW: workflow
    }


def create_new_work_description(persistence_store: pa.PersistenceAdaptor,
                                message_id: str,
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
    if not message_id:
        logger.error('Failed to build new work description, message_id should not be null or empty')
        raise ValueError('Expected message_id to not be None or empty')
    if workflow is None:
        logger.error('Failed to build new work description, workflow should not be null')
        raise ValueError('Expected workflow to not be None')
    if not inbound_status and not outbound_status:
        logger.error('Failed to build work description, expected inbound or outbound status to be present:'
                     '{inbound} {outbound}', fparams={'inbound': inbound_status, 'outbound': outbound_status})
        raise ValueError('Expected inbound/outbound to not be null')

    return WorkDescription(
        persistence_store,
        build_store_data(message_id, timing.get_time(), workflow, inbound_status, outbound_status))


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

        self._persistence_store = persistence_store
        self._from_store_data(store_data)

    async def publish(self):
        """
        Attempts to publish the local state of the work description to the state store
        :return:
        """
        await self._persistence_store.add(self.message_id, self._to_store_data())

    async def set_inbound_status(self, new_status: MessageStatus):
        """
        Helper method for setting the status and publishing to the state store

        :param new_status: new status to set
        """
        await self._set_status(INBOUND_STATUS, new_status)

    async def set_outbound_status(self, new_status: MessageStatus):
        """
        Helper method for setting the status and publishing to the state store

        :param new_status: new status to set
        """
        await self._set_status(OUTBOUND_STATUS, new_status)

    async def _set_status(self, field: str, new_status: MessageStatus):
        store_data = await self._persistence_store.update(self.message_id, {field: new_status})
        self._from_store_data(store_data)

    def _from_store_data(self, store_data):
        self.message_id = store_data[MESSAGE_ID]
        self.created_timestamp = store_data[CREATED_TIMESTAMP]
        self.inbound_status = store_data[INBOUND_STATUS]
        self.outbound_status = store_data[OUTBOUND_STATUS]
        self.workflow = store_data[WORKFLOW]

    def _to_store_data(self):
        return build_store_data(self.message_id, self.created_timestamp, self.workflow, self.inbound_status, self.outbound_status)
