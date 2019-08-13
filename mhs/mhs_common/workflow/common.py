"""This module defines the common base of all workflows."""
import abc
from typing import Tuple


class CommonWorkflow(abc.ABC):
    """Common functionality across all workflows."""

    @abc.abstractmethod
    async def handle_outbound_message(self, message_id: str, interaction_details: dict, payload: str) -> Tuple[int, str]:
        """
        Handle a message from the supplier system (or a message from an adaptor that the supplier system speaks to)
        that is to be sent outbound.

        :param message_id: ID of the message to send
        :param interaction_details: interaction details used to construct the message to send outbound
        :param payload: payload to send outbound
        :return: the HTTP status and body to return as a response
        """
        pass
