import uuid

import tornado.ioloop
import comms.queue_adaptor
import proton.reactor
import proton.handlers
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('PROTON_QUEUE')


class MessageSendingError(RuntimeError):
    pass


class ProtonQueueAdaptor(comms.queue_adaptor.QueueAdaptor):

    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs)
        self.host = kwargs.get('host')
        logger.info('000', 'Initialized proton queue adaptor for {host}', {'host': self.host})

    async def send(self, message: str):
        message_id = uuid.uuid4()
        msg = proton.Message(id=message_id, body=message)
        logger.info('001', 'Constructed message with {id} for {body}', {'id': message_id, 'body': message})
        await tornado.ioloop.IOLoop.current().run_in_executor(executor=None, func=lambda: self.__send(msg))

    def __send(self, message: proton.Message):
        proton.reactor.Container(ProtonMessagingHandler(self.host, message)).run()


class ProtonMessagingHandler(proton.handlers.MessagingHandler):

    def __init__(self, host, message: proton.Message):
        super(ProtonMessagingHandler, self).__init__()
        self.host = host
        self.message = message
        self.sender = None

    def on_start(self, event):
        logger.info('002', 'Establishing connection to {host} for sending messages.', {'host': self.host})
        self.sender = event.container.create_sender(self.host)

    def on_sendable(self, event):
        if event.sender.credit:
            event.sender.send(self.message)
            logger.info('003', 'Message sent to {host}.', {'host': self.host})
        else:
            logger.error('004', 'Failed to send message as no available credit.')
            raise MessageSendingError()

    def on_accepted(self, event):
        logger.info('005', 'Message received by {host}.', {'host': self.host})

    def on_disconnected(self, event):
        logger.info('006', 'Disconnected from {host}.', {'host': self.host})
