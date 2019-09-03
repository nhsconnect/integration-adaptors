"""This module defines the common base of all workflows."""
import abc
from typing import Tuple, Optional
import mhs_common.state.work_description as wd


class CommonWorkflow(abc.ABC):
    """Common functionality across all workflows."""

    @abc.abstractmethod
    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      work_description_object: Optional[wd.WorkDescription]
                                      ) -> Tuple[int, str]:
        """
        Handle a message from the supplier system (or a message from an adaptor that the supplier system speaks to)
        that is to be sent outbound.

        :param work_description_object: A potentially null value for the work description object for this message, if
                not present the child implementation is expected to generate this work description instance
        :param message_id: ID of the message to send
        :param correlation_id: correlation ID of the request
        :param interaction_details: interaction details used to construct the message to send outbound
        :param payload: payload to send outbound
        :return: the HTTP status and body to return as a response
        """
        pass

    @abc.abstractmethod
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        """
        Handles an inbound message from an external system (typically from spine)

        :param message_id: ID of the message the original request to Spine was made with
        :param correlation_id: correlation ID of the request
        :param work_description: work description object for the payload
        :param payload: payload to handle
        """
        pass
