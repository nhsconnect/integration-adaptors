"""This module defines the sync-async workflow."""
import asyncio
from typing import Tuple, Dict
from utilities import integration_adaptors_logger as log
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor as ta
from mhs_common.workflow import common_synchronous
from mhs_common.state import persistence_adaptor as pa
from exceptions import MaxRetriesExceeded
from mhs_common.workflow import common
from mhs_common import workflow
from mhs_common.workflow import sync_async_resynchroniser

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
                 work_description_store: pa.PersistenceAdaptor = None,
                 sync_async_store_max_retries: int = None,
                 sync_async_store_retry_delay: int = None,
                 resynchroniser: sync_async_resynchroniser.SyncAsyncResynchroniser = None
                 ):
        """Create a new SyncAsyncWorkflow that uses the specified dependencies to load config, build a message and
        send it.
        :param transmission: The component that can be used to send messages.
        :param sync_async_store: The resynchronisor state store
        :param party_id: The party ID of this MHS. Sent in ebXML requests.
        """

        self.transmission = transmission
        self.sync_async_store = sync_async_store
        self.work_description_store = work_description_store
        self.party_id = party_id
        self.resynchroniser = resynchroniser
        self.sync_async_store_max_retries = sync_async_store_max_retries
        self.sync_async_store_retry_delay = sync_async_store_retry_delay / 1000 if sync_async_store_retry_delay \
            else None

    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      work_description: wd.WorkDescription
                                      ) -> Tuple[int, str]:
        raise NotImplementedError("This method is not implemented for the sync-async workflow, consider using"
                                  "`self.handle_sync_async_message` instead")

    async def handle_sync_async_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                                 payload: str,
                                                 async_workflow: common.CommonWorkflow
                                                 ) -> Tuple[int, str, wd.WorkDescription]:

        logger.info('0001', 'Entered sync-async workflow to handle outbound message')
        wdo = wd.create_new_work_description(self.work_description_store, message_id,
                                             wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                                             workflow.SYNC_ASYNC)

        status_code, response = await async_workflow.handle_outbound_message(message_id, correlation_id,
                                                                             interaction_details, payload, wdo)
        if not (status_code == 202):
            logger.info('0002', 'No ACK received ')
            return status_code, response, wdo

        status_code, response = await self._retrieve_async_response(message_id, wdo)
        return status_code, response, wdo

    async def _retrieve_async_response(self, message_id, wdo: wd.WorkDescription):
        try:
            response = await self.resynchroniser.pause_request(message_id)
            log.correlation_id.set(response[CORRELATION_ID])
            logger.info('0003', 'Retrieved async response from sync-async store, set correlation ID')
            await self._update_state_store_success_retriaval(wdo)
            return 200, response[MESSAGE_DATA]
        except sync_async_resynchroniser.SyncAsyncResponseException as e:
            logger.error('0004', 'No async response placed on async store within timeout for {messageId}',
                         {'messageId': message_id})
            return 500, "No async response received from sync-async store"

    async def _update_state_store_success_retriaval(self, wdo):
        attempts = 0
        while attempts < 4:
            try:
                await wdo.update()
                await wdo.set_status(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_LOADED)
                break
            except wd.OutOfDateVersionError as e:
                logger.error('0021', 'Failed attempt to update state store')
                if attempts == 3:
                    raise e
                else:
                    attempts += 1



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
