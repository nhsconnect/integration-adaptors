import comms.queue_adaptor
import proton.handlers


class ProtonQueueAdaptor(comms.queue_adaptor.QueueAdaptor):

    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs)
        self.message_handler = ProtonMessagingHandler()

    async def send(self, message):
        pass


class ProtonMessagingHandler(proton.handlers.MessagingHandler):

    def __init__(self, prefetch=10, auto_accept=True, auto_settle=True, peer_close_is_error=False):
        super().__init__(prefetch, auto_accept, auto_settle, peer_close_is_error)

    def keep_sending(self):
        return True