import asyncio

from utilities import integration_adaptors_logger as log

from retry import retriable_action
from persistence import persistence_adaptor

logger = log.IntegrationAdaptorsLogger(__name__)


class SyncAsyncResponseException(Exception):
    pass


class SyncAsyncResynchroniser(object):

    def __init__(self, sync_async_store: persistence_adaptor.PersistenceAdaptor,
                 max_retries: int,
                 retry_interval: float,
                 initial_delay: float
                 ):
        """
        :param sync_async_store: The store where the sync-async messages are placed from the inbound service
        :param max_retries: The total number of polling attempts to the sync async store while attempting to resynchronise
        :param retry_interval: The time between polling requests to the sync-async store in seconds
        :param initial_delay: The time to wait before making the first request to the sync async store in seconds
        """
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.sync_async_store = sync_async_store
        self.initial_delay = initial_delay

    async def pause_request(self, message_id: str) -> dict:
        logger.info('Beginning async retrieval from sync-async store')

        await asyncio.sleep(self.initial_delay)

        retry_result = await retriable_action.RetriableAction(lambda: self.sync_async_store.get(message_id),
                                                              self.max_retries, self.retry_interval) \
            .with_success_check(lambda i: i is not None) \
            .with_retriable_exception_check(lambda e: e is None) \
            .execute()

        if not retry_result.is_successful:
            logger.error('Resync retries exceeded. {max_retries}', fparams={'max_retries': self.max_retries})
            raise SyncAsyncResponseException('Polling on the sync async store timed out')

        return retry_result.result
