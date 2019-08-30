"""Module for Proton specific queue adaptor functionality. """

from typing import Dict, Any

import proton.handlers
import proton.reactor
import tornado.ioloop

import comms.queue_adaptor
import utilities.integration_adaptors_logger as log
import utilities.message_utilities

logger = log.IntegrationAdaptorsLogger('PROTON_QUEUE')


class MessageSendingError(RuntimeError):
    """An error occurred whilst sending a message to the Message Queue"""
    pass


class EarlyDisconnectError(RuntimeError):
    """The connection to the Message Queue ended before sending of the message had been done."""
    pass


class ProtonQueueAdaptor(comms.queue_adaptor.QueueAdaptor):
    """Proton implementation of a queue adaptor."""

    def __init__(self, **kwargs) -> None:
        """
        Construct a Proton implementation of a :class:`QueueAdaptor <comms.queue_adaptor.QueueAdaptor>`.
        The kwargs provided should contain the following information:
          * host: The host of the Message Queue to be interacted with.
          * username: The username to use to connect to the Message Queue.
          * password The password to use to connect to the Message Queue.
        :param kwargs: The key word arguments required for this constructor.
        """
        super().__init__()
        self.host = kwargs.get('host')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        logger.info('000', 'Initialized proton queue adaptor for {host}', {'host': self.host})

    async def send_async(self, message: str, properties: Dict[str, Any] = None) -> None:
        logger.info('008', 'Sending message asynchronously.')
        payload = self.__construct_message(message, properties=properties)
        await tornado.ioloop.IOLoop.current() \
            .run_in_executor(executor=None, func=lambda: self.__send(payload))

    def send_sync(self, message: str, properties: Dict[str, Any] = None) -> None:
        logger.info('009', 'Sending message synchronously.')
        payload = self.__construct_message(message, properties=properties)
        self.__send(payload)

    @staticmethod
    def __construct_message(message: str, properties: Dict[str, Any] = None) -> proton.Message:
        """
        Build a message with a generated uuid, and specified message body.
        :param message: The message body to be wrapped.
        :param properties: Optional application properties to send with the message.
        :return: The Message in the correct format with generated uuid.
        """
        message_id = utilities.message_utilities.MessageUtilities.get_uuid()
        logger.info('001', 'Constructing message with {id} for {body} and {applicationProperties}',
                    {'id': message_id, 'body': message, 'applicationProperties': properties})
        return proton.Message(id=message_id, body=message, properties=properties)

    def __send(self, message: proton.Message) -> None:
        """
        Performs a synchronous send of a message, to the host defined when this adaptor was constructed.
        :param message: The message to be sent.
        """
        proton.reactor.Container(ProtonMessagingHandler(self.host, self.username, self.password, message)).run()


class ProtonMessagingHandler(proton.handlers.MessagingHandler):
    """Implementation of a Proton MessagingHandler which will send a single message."""

    def __init__(self, host: str, username: str, password: str, message: proton.Message) -> None:
        """
        Constructs a MessagingHandler which will send a specified message to a specified host.
        :param host: The host to send the message to.
        :param username: The username to login to the host with.
        :param password: The password to login to the host with.
        :param message: The message to be sent to the host.
        """
        super().__init__()
        self._host = host
        self._username = username
        self._password = password
        self._message = message
        self._sender = None
        self._sent = False

    def on_start(self, event):
        logger.info('002', 'Establishing connection to {host} for sending messages.', {'host': self._host})
        self._sender = event.container.create_sender(proton.Url(self._host, username=self._username,
                                                                password=self._password))

    def on_sendable(self, event):
        if event.sender.credit:
            if not self._sent:
                event.sender.send(self._message)
                logger.info('003', 'Message sent to {host}.', {'host': self._host})
                self._sent = True
        else:
            logger.error('004', 'Failed to send message as no available credit.')
            raise MessageSendingError()

    def on_accepted(self, event):
        logger.info('005', 'Message received by {host}.', {'host': self._host})
        event.connection.close()

    def on_disconnected(self, event):
        logger.info('006', 'Disconnected from {host}.', {'host': self._host})
        if not self._sent:
            logger.error('010', 'Disconnected before message could be sent.')
            raise EarlyDisconnectError()

    def on_rejected(self, event):
        logger.warning('007', 'Message rejected by {host}.', {'host': self._host})
        self._sent = False
