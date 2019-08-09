"""Module for generic queue adaptor functionality"""
import abc


class QueueAdaptor(abc.ABC):
    """Interface for a message queue adaptor."""

    @abc.abstractmethod
    async def send_async(self, message: str) -> None:
        """
        Sends a message with awaits using the async flow.
        :param message: The message content to send.
        """
        pass

    @abc.abstractmethod
    def send_sync(self, message: str) -> None:
        """
        Sends a message and blocks waiting for the send to complete.
        :param message: The message content to send.
        """
        pass
