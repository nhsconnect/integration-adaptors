import tornado
import tornado.gen
from mhs_common.state import persistence_adaptor
from utilities import integration_adaptors_logger as log
import asyncio

logger = log.IntegrationAdaptorsLogger('RESYNCHRONISER')


class SyncAsyncResponseException(Exception):
    pass


class SyncAsyncResynchroniser:

    def __init__(self, sync_async_store: persistence_adaptor.PersistenceAdaptor,
                 max_retries: int,
                 retry_interval: float
                 ):
        """
        :param sync_async_store: The store where the sync-async messages are placed from the inbound service
        :param max_retries: The total number of polling attempts to the sync async store while attempting to resynchronise
        :param retry_interval: The time between polling requests to the sync-async store in milliseconds
        """
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.sync_async_store = sync_async_store

    async def pause_request(self, message_id: str) -> dict:
        retries = 0
        logger.info('001', 'Beginning async retrieval from sync-async store')
        while retries < self.max_retries:
            item = await self.sync_async_store.get(message_id)
            if item is not None:
                logger.info('002', 'Message found in sync-async store, ending polling')
                return item
            logger.warning('003', f'Failed to find async response after {retries} of {self.max_retries}')
            retries += 1

            if not (retries == self.max_retries):
                await asyncio.sleep(self.retry_interval)

        logger.error('004', 'Resync retries exceeded, attempted {retries}', {'retries': retries})
        raise SyncAsyncResponseException('Polling on the sync async store timed out')
