"""Module for Proton specific queue adaptor functionality. """
import json
from typing import Dict, Any, List

import proton.handlers
import proton.reactor

import comms.queue_adaptor
import utilities.integration_adaptors_logger as log
import utilities.message_utilities as message_utilities
from exceptions import MaxRetriesExceeded
from retry.retriable_action import RetriableAction

logger = log.IntegrationAdaptorsLogger(__name__)


class MessageSendingError(RuntimeError):
    """An error occurred whilst sending a message to the Message Queue"""
    pass


class EarlyDisconnectError(RuntimeError):
    """The connection to the Message Queue ended before sending of the message had been done."""
    pass


class ProtonQueueAdaptor(comms.queue_adaptor.QueueAdaptor):
    """Proton implementation of a queue adaptor."""

    def __init__(self, urls: List[str], queue: str, username, password, max_retries=0, retry_delay=0) -> None:
        """
        Construct a Proton implementation of a :class:`QueueAdaptor <comms.queue_adaptor.QueueAdaptor>`.
        The kwargs provided should contain the following information:
          * host: The host of the Message Queue to be interacted with.
          * username: The username to use to connect to the Message Queue.
          * password The password to use to connect to the Message Queue.
        :param kwargs: The key word arguments required for this constructor.
        """
        super().__init__()
        self.urls = urls
        self.queue = queue
        self.username = username
        self.password = password
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        if self.urls is None or not isinstance(urls, List) or len(urls) == 0:
            raise ValueError("Invalid urls %s", urls)
        if queue is None or len(queue.strip()) == 0:
            raise ValueError("Invalid queue name %s", queue)

        logger.info('Initialized proton queue adaptor for {urls} with {max_retries} and {retry_delay}',
                    fparams={'urls': self.urls, 'max_retries': max_retries, 'retry_delay': retry_delay})

    async def send_async(self, message: dict, properties: Dict[str, Any] = None) -> None:
        """Builds and asynchronously sends a message to the host defined when this adaptor was constructed. Raises an
        exception to indicate that the message could not be sent successfully.

        :param message: The message body to send. This will be serialised as JSON.
        :param properties: Optional application properties to send with the message.
        """
        logger.info('Sending message asynchronously.')
        payload = self.__construct_message(message, properties=properties)
        try:
            await self.__send_with_retries(payload)
        except MaxRetriesExceeded as e:
            raise MessageSendingError() from e

    @staticmethod
    def __construct_message(message: dict, properties: Dict[str, Any] = None) -> proton.Message:
        """
        Build a message with a generated uuid, and specified message body.
        :param message: The message body to be wrapped.
        :param properties: Optional application properties to send with the message.
        :return: The Message in the correct format with generated uuid.
        """
        message_id = message_utilities.get_uuid()
        logger.info('Constructing message with {id} and {applicationProperties}',
                    fparams={'id': message_id, 'applicationProperties': properties})
        return proton.Message(id=message_id,
                              content_type='application/json',
                              body=json.dumps(message),
                              properties=properties)

    async def __try_sending_to_all_in_sequence(self, message: proton.Message) -> None:
        """
        Sends message to ONE of available brokers trying each in sequence. Raises exception if none succeeds.
        :param message: message to send
        """
        exception = None
        for url in self.urls:
            try:
                logger.info("Trying to send message to {url} {queue}", fparams={'url': url, 'queue': self.queue})
                messaging_handler = ProtonMessagingHandler(url, self.queue, self.username, self.password, message)
                proton.reactor.Container(messaging_handler).run()
            except EarlyDisconnectError as e:
                logger.warning("Failed to send message to '%s", url)
                exception = e
            else:
                exception = None
                break
        if exception:
            logger.warning("Failed to send message to any of '%s", self.urls)
            raise exception

    async def __send_with_retries(self, message: proton.Message) -> None:
        """
        Performs a synchronous send of a message, to the host defined when this adaptor was constructed.
        :param message: The message to be sent.
        """
        result = await RetriableAction(
            lambda: self.__try_sending_to_all_in_sequence(message),
            self.max_retries,
            self.retry_delay)\
            .with_retriable_exception_check(lambda ex: isinstance(ex, EarlyDisconnectError))\
            .execute()

        if not result.is_successful:
            logger.error("Exceeded the maximum number of retries, {max_retries} retries, when putting "
                         "message onto inbound queue",
                         fparams={"max_retries": self.max_retries})
            raise MaxRetriesExceeded('The max number of retries to put a message onto the inbound queue has '
                                     'been exceeded') from result.exception


class ProtonMessagingHandler(proton.handlers.MessagingHandler):
    """Implementation of a Proton MessagingHandler which will send a single message. Note that this class will raise
    an exception to indicate that a message could not be sent successfully."""

    def __init__(self, url: str, queue: str, username: str, password: str, message: proton.Message) -> None:
        """
        Constructs a MessagingHandler which will send a specified message to a specified host.
        :param url: The host to send the message to.
        :param username: The username to login to the host with.
        :param password: The password to login to the host with.
        :param message: The message to be sent to the host.
        """
        super().__init__()
        self._url = url
        self._queue = queue
        self._username = username
        self._password = password
        self._message = message
        self._sent = False

    def on_start(self, event: proton.Event) -> None:
        """Called when this messaging handler is started.

        :param event: The start event.
        """
        logger.info('Establishing connection to {url} for sending messages.', fparams={'url': self._url})
        conn = event.container.connect(url=self._url, user=self._username, password=self._password, reconnect=False)
        event.container.create_sender(conn, target=self._queue)

    def on_sendable(self, event: proton.Event) -> None:
        """Called when the link is ready for sending messages.

        :param event: The sendable event.
        """
        if event.sender.credit:
            if not self._sent:
                event.sender.send(self._message)
                logger.info('Message sent to {url}.', fparams={'url': event.connection.connected_address})
                self._sent = True
        else:
            logger.error('Failed to send message as no available credit.')
            raise MessageSendingError()

    def on_accepted(self, event: proton.Event) -> None:
        """Called when the outgoing message is accepted by the remote peer.

        :param event: The accepted event.
        """
        logger.info('Message received by {url}.', fparams={'url': event.connection.connected_address})
        event.connection.close()

    def on_disconnected(self, event: proton.Event) -> None:
        """Called when the socket is disconnected.

        :param event: The disconnect event.
        """
        logger.info('Disconnected from {url}.', fparams={'url': event.connection.connected_address})
        if not self._sent:
            logger.error('Disconnected before message could be sent.')
            raise EarlyDisconnectError()

    def on_rejected(self, event: proton.Event) -> None:
        """Called when the outgoing message is rejected by the remote peer.

        :param event:
        :return:
        """
        logger.warning('Message rejected by {url}.', fparams={'url': self._url})
        self._sent = False

    def on_transport_error(self, event: proton.Event) -> None:
        """Called when an error is encountered with the transport over which the AMQP connection is established.

        :param event: The transport error event.
        """
        logger.error("There was an error with the transport used for the connection to {url}.",
                     fparams={'url': event.connection.connected_address})
        super().on_transport_error(event)
        raise EarlyDisconnectError()

    def on_connection_error(self, event: proton.Event) -> None:
        """Called when the peer closes the connection with an error condition.

        :param event: The connection error event.
        """
        logger.error("{url} closed the connection with an error. {remote_condition}",
                     fparams={'url': event.connection.connected_address, 'remote_condition': event.context.remote_condition})
        super().on_connection_error(event)
        raise EarlyDisconnectError()

    def on_session_error(self, event: proton.Event) -> None:
        """Called when the peer closes the session with an error condition.

        :param event: The session error event.
        """
        logger.error("{url} closed the session with an error. {remote_condition}",
                     fparams={'url': event.connection.connected_address, 'remote_condition': event.context.remote_condition})
        super().on_session_error(event)
        raise EarlyDisconnectError()

    def on_link_error(self, event: proton.Event) -> None:
        """Called when the peer closes the link with an error condition.

        :param event: The link error event.
        """
        logger.error("{url} closed the link with an error. {remote_condition}",
                     fparams={'url': event.connection.connected_address, 'remote_condition': event.context.remote_condition})
        super().on_link_error(event)
        raise EarlyDisconnectError()
