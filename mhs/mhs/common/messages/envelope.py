"""This module defines the base envelope used to wrap messages to be sent to a remote MHS."""
import abc


class Envelope(abc.ABC):
    """An envelope that contains a message to be sent to a remote MHS."""

    @abc.abstractmethod
    def serialize(self):
        """Produce a serialised representation of this message.

        :return: The serialized representation of this message.
        """
        pass
