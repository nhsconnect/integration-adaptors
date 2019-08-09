"""This module defines the common base of all workflows."""
import abc
from typing import Tuple


class UnknownInteractionError(Exception):
    """Raised when an unknown interaction has been specified"""

    def __init__(self, interaction_name):
        """Create a new UnknownInteractionError for the specified interaction name.

        :param interaction_name: The interaction name requested but not found.
        """
        self.interaction_name = interaction_name


class CommonWorkflow(abc.ABC):
    """Common functionality across all workflows."""

    @abc.abstractmethod
    async def handle_supplier_message(self, message_id: str, interaction_details: dict, payload: str) -> Tuple[int, str]:
        """
        Handle a message from the supplier system (or a message from an adaptor that the supplier system speaks to).

        :param message_id: ID of the message to send
        :param interaction_details: interaction details used to construct the message to send downstream
        :param payload: payload to send downstream
        :return: the HTTP status and body to return as a response
        """
        pass
