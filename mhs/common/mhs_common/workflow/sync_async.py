"""This module defines the sync-async workflow."""
from typing import Tuple, Optional

from mhs_common import workflow
from mhs_common.state import work_description as wd
from mhs_common.workflow import common
from mhs_common.workflow import common_synchronous
from mhs_common.workflow import sync_async_resynchroniser
from mhs_common.workflow.common import MessageData
from persistence import persistence_adaptor as pa
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

ASYNC_RESPONSE_EXPECTED = 'async_response_expected'
MESSAGE_ID = 'MESSAGE_ID'
MESSAGE_DATA = 'DATA'
CORRELATION_ID = 'CORRELATION_ID'


class SyncAsyncStoreFailure(RuntimeError):
    """Exception thrown when data could not be added to the sync async store."""
    pass


class SyncAsyncWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the sync-async messaging pattern."""

    def __init__(self,
                 sync_async_store: pa.PersistenceAdaptor = None,
                 work_description_store: pa.PersistenceAdaptor = None,
                 resynchroniser: sync_async_resynchroniser.SyncAsyncResynchroniser = None,
                 ):
        """Create a new SyncAsyncWorkflow that uses the specified dependencies to load config, build a message and
        send it.
        :param sync_async_store: The resynchronisor state store
        :param work_description_store: The persistence store instance that holds the work description data
        :param sync_async_store_retry_delay: time between sync async store publish attempts
        :param persistence_store_max_retries: number of times to retry publishing something to a persistence store
        """
        super().__init__()
        self.sync_async_store = sync_async_store
        self.work_description_store = work_description_store
        self.resynchroniser = resynchroniser
        self.workflow_name = workflow.SYNC_ASYNC

    async def handle_outbound_message(self, from_asid: Optional[str],
                                      message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      work_description: wd.WorkDescription
                                      ) -> Tuple[int, str]:
        raise NotImplementedError("This method is not implemented for the sync-async workflow, consider using"
                                  "`self.handle_sync_async_outbound_message` instead")

    async def handle_sync_async_outbound_message(self, from_asid: Optional[str], message_id: str, correlation_id: str,
                                                 interaction_details: dict,
                                                 payload: str,
                                                 async_workflow: common.CommonWorkflow
                                                 ) -> Tuple[int, str, wd.WorkDescription]:

        logger.info('Entered sync-async workflow to handle outbound message')
        wdo = wd.create_new_work_description(self.work_description_store, message_id,
                                             workflow.SYNC_ASYNC,
                                             outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)
        await wdo.publish()

        status_code, response, _ = await async_workflow.handle_outbound_message(from_asid, message_id, correlation_id,
                                                                                interaction_details, payload, wdo)
        if not status_code == 202:
            logger.warning('No ACK received ')
            return status_code, response, wdo

        status_code, response = await self._retrieve_async_response(message_id, wdo)
        return status_code, response, wdo

    async def _retrieve_async_response(self, message_id, wdo: wd.WorkDescription):
        logger.info('Attempting to retrieve the async response from the async store')
        try:
            response = await self.resynchroniser.pause_request(message_id)
            logger.info('Retrieved async response from sync-async store')
            return 200, response[MESSAGE_DATA]
        except sync_async_resynchroniser.SyncAsyncResponseException:
            logger.error('No async response placed on async store within timeout for {messageId}',
                         fparams={'messageId': message_id})
            return 500, "No async response received from sync-async store"

    async def handle_inbound_message(self, message_id: str, correlation_id: str, wdo: wd.WorkDescription, message_data: MessageData):
        logger.info('Entered sync-async inbound workflow')

        try:
            await self.sync_async_store.add(message_id, {MESSAGE_ID: message_id, CORRELATION_ID: correlation_id, MESSAGE_DATA: message_data.payload})
            logger.info('Placed message in sync-async store successfully')
            await wdo.set_inbound_status(wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_STORED)
        except Exception as e:
            logger.error('Failed to write to sync-async store')
            await wdo.set_inbound_status(wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_BE_STORED)
            raise e

    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED)

    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND)
