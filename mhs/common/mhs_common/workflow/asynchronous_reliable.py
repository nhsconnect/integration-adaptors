"""This module defines the asynchronous reliable workflow."""
from typing import Tuple, Optional

from mhs_common.workflow import common_asynchronous
from mhs_common.state import work_description as wd


class AsynchronousReliableWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous reliable messaging pattern."""

    async def handle_outbound_message(self, from_asid: Optional[str],
                                      message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      work_description_object: Optional[wd.WorkDescription])\
            -> Tuple[int, str, Optional[wd.WorkDescription]]:
        raise NotImplementedError()

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        raise NotImplementedError()

    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        raise NotImplementedError()

    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        raise NotImplementedError()
