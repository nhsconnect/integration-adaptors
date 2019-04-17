"""A module that defines the MessageBuilder abstract class, used as the interface for all message builders."""

from abc import abstractmethod, ABC


class MessageBuilder(ABC):
    """A class that can be used to build a message suitable for sending to a remote MHS."""

    @abstractmethod
    def build_message(self, message_dictionary):
        """Build a message using the values provided in the message dictionary to populate it.

        :param message_dictionary: A dictionary of values to be used when building the message.
        :return: A string containing a message suitable for sending to a remote MHS.
        """
        pass
