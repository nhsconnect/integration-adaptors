"""This module defines the base envelope used to wrap messages to be sent to a remote MHS."""

from __future__ import annotations

import abc
from typing import Dict, Tuple


class Envelope(abc.ABC):
    """An envelope that contains a message to be sent to a remote MHS."""

    @abc.abstractmethod
    def serialize(self) -> Tuple[str, Dict[str, str], str]:
        """Produce a serialised representation of this message.

        :return: A tuple of: the message id, headers to send along with the message and the serialized representation
        of the message.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> Envelope:
        """Parse the provided message string and create an instance of an Envelope.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: An instance of an Envelope constructed from the message.
        """
        pass
