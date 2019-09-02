import tornado
import tornado.gen
from mhs_common.state import persistence_adaptor


class SyncAsyncResponseException(Exception):
    pass


class SyncAsyncResynchroniser:

    def __init__(self, sync_async_store: persistence_adaptor.PersistenceAdaptor,
                 retry_timeout: int,
                 retry_interval: int
                 ):
        """

        :param sync_async_store: The store where the sync-async messages are placed from the inbound service
        :param retry_timeout: The total time to poll the sync-async store for a async response in seconds
        :param retry_interval: The time between polling requests to the sync-async store in milliseconds
        """
        self.retry_timeout = retry_timeout
        self.retry_interval = retry_interval / 1000
        self.sync_async_store = sync_async_store

    async def pause_request(self, message_id: str) -> dict:
        time_waited = 0
        while time_waited < self.retry_timeout:
            item = await self.sync_async_store.get(message_id)
            if item is not None:
                return item
            await tornado.gen.sleep(self.retry_interval)
            time_waited += self.retry_interval
        raise SyncAsyncResponseException('Polling on the sync async store timed out')
