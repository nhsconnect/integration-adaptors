"""This module defines the synchronous workflow."""
from typing import Tuple

from mhs_common.workflow import common_synchronous
import mhs_common.state.work_description as wd


class SynchronousWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the synchronous messaging pattern."""

    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        raise NotImplementedError()

    async def handle_inbound_message(self, work_description: wd.WorkDescription, payload: str):
        raise NotImplementedError()
