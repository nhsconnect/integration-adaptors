import uuid

import tornado.ioloop
import comms.queue_adaptor
import proton.reactor
import proton.handlers
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('PROTON_QUEUE')


class MessageSendingError(RuntimeError):
    pass


class EarlyDisconnectError(RuntimeError):
    pass


class ProtonQueueAdaptor(comms.queue_adaptor.QueueAdaptor):

    def __init__(self, **kwargs) -> None:
        super(ProtonQueueAdaptor, self).__init__()
        self.host = kwargs.get('host')
        logger.info('000', 'Initialized proton queue adaptor for {host}', {'host': self.host})

    async def send_async(self, message: str):
        logger.info('008', 'Sending message asynchronously.')
        await tornado.ioloop.IOLoop.current() \
            .run_in_executor(executor=None, func=lambda: self.__send(self.__construct_message(message)))

    def send_sync(self, message: str):
        logger.info('009', 'Sending message synchronously.')
        self.__send(self.__construct_message(message))

    @staticmethod
    def __construct_message(message: str) -> proton.Message:
        message_id = str(uuid.uuid4())
        logger.info('001', 'Constructing message with {id} for {body}', {'id': message_id, 'body': message})
        return proton.Message(id=message_id, body=message)

    def __send(self, message: proton.Message):
        proton.reactor.Container(ProtonMessagingHandler(self.host, message)).run()


class ProtonMessagingHandler(proton.handlers.MessagingHandler):

    def __init__(self, host, message: proton.Message):
        super(ProtonMessagingHandler, self).__init__()
        self.host = host
        self.message = message
        self.sender = None
        self.sent = False

    def on_start(self, event):
        logger.info('002', 'Establishing connection to {host} for sending messages.', {'host': self.host})
        self.sender = event.container.create_sender(self.host)

    def on_sendable(self, event):
        if event.sender.credit:
            if not self.sent:
                event.sender.send(self.message)
                logger.info('003', 'Message sent to {host}.', {'host': self.host})
                self.sent = True
        else:
            logger.error('004', 'Failed to send message as no available credit.')
            raise MessageSendingError()

    def on_accepted(self, event):
        logger.info('005', 'Message received by {host}.', {'host': self.host})
        event.connection.close()

    def on_disconnected(self, event):
        logger.info('006', 'Disconnected from {host}.', {'host': self.host})
        if not self.sent:
            logger.error('010', 'Disconnected before message could be sent.')
            raise EarlyDisconnectError()

    def on_rejected(self, event):
        logger.warning('007', 'Message rejected by {host}.', {'host': self.host})
        self.sent = False
