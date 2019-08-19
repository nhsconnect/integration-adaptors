"""This module defines the common base of all workflows."""
import abc
from typing import Tuple
import mhs_common.state.work_description as wd


class CommonWorkflow(abc.ABC):
    """Common functionality across all workflows."""

    @abc.abstractmethod
    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        """
        Handle a message from the supplier system (or a message from an adaptor that the supplier system speaks to)
        that is to be sent outbound.

        :param message_id: ID of the message to send
        :param correlation_id: correlation ID of the request
        :param interaction_details: interaction details used to construct the message to send outbound
        :param payload: payload to send outbound
        :return: the HTTP status and body to return as a response
        """
        pass

    @abc.abstractmethod
    async def handle_inbound_message(self, work_description: wd.WorkDescription, payload: str):
        """
        Handles an inbound message from an external system (typically from spine)

        :param work_description: work description object for the payload
        :param payload: payload to handle
        """
        pass
