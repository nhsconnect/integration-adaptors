"""This module defines the sync-async workflow."""

from typing import Tuple
from utilities import integration_adaptors_logger as log
from mhs_common.state import work_description as wd
from mhs_common.workflow import common_synchronous, common_asynchronous
import copy
import asyncio
from typing import Tuple, Dict
from utilities import integration_adaptors_logger as log, message_utilities
import mhs_common.messages.ebxml_envelope as ebxml_envelope
import mhs_common.messages.ebxml_request_envelope as ebxml_request_envelope
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor as ta
from mhs_common.workflow import common_synchronous
from mhs_common.state import persistence_adaptor as pa
from exceptions import MaxRetriesExceeded


logger = log.IntegrationAdaptorsLogger('MHS_SYNC_ASYNC_WORKFLOW')

ASYNC_RESPONSE_EXPECTED = 'async_response_expected'
MESSAGE_DATA = 'data'
CORRELATION_ID = 'correlation_id'


class SyncAsyncWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the sync-async messaging pattern."""

    def __init__(self,
                 party_id: str,
                 transmission: ta.TransmissionAdaptor = None,
                 sync_async_store: pa.PersistenceAdaptor = None,
                 sync_async_store_max_retries: int = None,
                 sync_async_store_retry_delay: int = None
                 ):
        """Create a new SyncAsyncWorkflow that uses the specified dependencies to load config, build a message and
        send it.
        :param transmission: The component that can be used to send messages.
        :param sync_async_store: The resynchronisor state store
        :param party_id: The party ID of this MHS. Sent in ebXML requests.
        """

        self.transmission = transmission
        self.sync_async_store = sync_async_store
        self.party_id = party_id
        self.sync_async_store_max_retries = sync_async_store_max_retries
        self.sync_async_store_retry_delay = sync_async_store_retry_delay / 1000 if sync_async_store_retry_delay \
            else None


    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        return await self.workflow.handle_outbound_message(message_id, correlation_id, interaction_details, payload)
        # TODO-look at return value, if it's an ack, then pause request, else passthrough error
        # TODO-when request resumes, return response it resumed with

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('001', 'Entered sync-async inbound workflow')
        await work_description.set_status(wd.MessageStatus.INBOUND_RESPONSE_RECEIVED)

        try:
            await self._add_to_sync_async_store(message_id, {CORRELATION_ID: correlation_id, MESSAGE_DATA: payload})
            logger.info('004', 'Placed message onto inbound queue successfully')
            await work_description.set_status(wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_STORED)
        except Exception as e:
            logger.error('005', 'Failed to write to sync-async store')
            await work_description.set_status(wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED)
            raise e

    async def _add_to_sync_async_store(self, key, data):
        logger.info('002', 'Attempting to add inbound message to sync-async store')
        retry = self.sync_async_store_max_retries
        while True:
            try:
                await self.sync_async_store.add(key, data)
                logger.info('003', 'Successfully updated state store')
                break
            except Exception as e:
                logger.warning('021', 'Exception raised while adding to sync-async store {exception} {retry}',
                               {'exception': e, 'retry': retry})
                retry -= 1
                if retry == 0:
                    logger.warning('022', 'Final retry has been attempted for adding message to sync async store')
                    raise MaxRetriesExceeded('Max number of retries exceeded whilst attempting to put the message'
                                             'on the sync-async store') from e
                
                await asyncio.sleep(self.sync_async_store_retry_delay)

