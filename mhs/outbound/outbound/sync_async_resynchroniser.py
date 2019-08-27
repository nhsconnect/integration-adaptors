import tornado
import tornado.gen
from mhs_common.state import persistence_adaptor


class SyncAsyncResynchroniser:

    def __init__(self, persistence_store: persistence_adaptor.PersistenceAdaptor):
        self.persistence_store = persistence_store

    async def pause_request(self, message_id: str) -> str:
        # For each request, we poll the table independently, waiting for the event to pop up
        # TODO-would be better to do a batch get, though more complicated

        retries = 0
        while retries < 10: # TODO-should be configurable
            item = await self.persistence_store.get(message_id)
            if item is not None:
                return item
            retries += 1
            await tornado.gen.sleep(0.1) # TODO-should be configurable
        raise Exception('Timed out waiting for response') # TODO-should be a better exception
