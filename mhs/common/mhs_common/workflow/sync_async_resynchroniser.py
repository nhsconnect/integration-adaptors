import tornado
import tornado.gen
from mhs_common.state import persistence_adaptor
from utilities import integration_adaptors_logger as log


logger = log.IntegrationAdaptorsLogger('RESYNCHRONISER')


class SyncAsyncResponseException(Exception):
    pass


class SyncAsyncResynchroniser:

    def __init__(self, sync_async_store: persistence_adaptor.PersistenceAdaptor,
                 retry_timeout: int,
                 retry_interval: float
                 ):
        """
        :param sync_async_store: The store where the sync-async messages are placed from the inbound service
        :param retry_timeout: The total time to poll the sync-async store for a async response in seconds
        :param retry_interval: The time between polling requests to the sync-async store in milliseconds
        """
        self.retry_timeout = retry_timeout
        self.retry_interval = retry_interval
        self.sync_async_store = sync_async_store

    async def pause_request(self, message_id: str) -> dict:
        time_waited = 0
        logger.info('001', 'Beginning async retrieval from sync-async store')
        while time_waited < self.retry_timeout:
            item = await self.sync_async_store.get(message_id)
            if item is not None:
                logger.info('002', 'Message found in sync-async store, ending polling')
                return item
            logger.info('003', 'Failed to find async response after {time}s', {'time': time_waited})
            await tornado.gen.sleep(self.retry_interval)

            time_waited += self.retry_interval
        logger.error('004', 'Resync timer exceeded, waited {time}s', {'time': time_waited})
        raise SyncAsyncResponseException('Polling on the sync async store timed out')
