"""Module for generic queue adaptor functionality"""
import abc
from typing import Dict, Any


class QueueAdaptor(abc.ABC):
    """Interface for a message queue adaptor."""

    @abc.abstractmethod
    async def send_async(self, message: dict, properties: Dict[str, Any] = None) -> None:
        """
        Sends a message which awaits using the async flow.
        :param message: The message content to send. This will be serialised as JSON.
        :param properties: Optional additional properties to send with the message.
        """
        pass
