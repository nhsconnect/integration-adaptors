"""This module defines the asynchronous express workflow."""
from typing import Tuple

from mhs_common.workflow import common_asynchronous
from mhs_common.state import work_description as wd


class AsynchronousExpressWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous express messaging pattern."""

    async def handle_outbound_message(self, message_id: str, interaction_details: dict, payload: str) \
            -> Tuple[int, str]:
        raise NotImplementedError()

    async def handle_inbound_message(self, work_description: wd.WorkDescription, payload: str):
        pass
