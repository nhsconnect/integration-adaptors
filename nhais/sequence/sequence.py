import abc
from typing import Optional


class SequenceGenerator(abc.ABC):
    """A component that provides a common interface to generate a sequence of numbers."""

    @abc.abstractmethod
    async def next(self, key: str) -> Optional[dict]:
        """Produces the next number in the sequence.

        :param key: The key used to identify the sequence.
        :return: The next number in the sequence
        """
        pass