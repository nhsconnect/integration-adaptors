"""This module defines the synchronous workflow."""
from typing import Tuple

import workflow.common_synchronous as common_synchronous


class SynchronousWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the synchronous messaging pattern."""

    async def handle_outbound_message(self, message_id: str, interaction_details: dict, payload: str) \
            -> Tuple[int, str]:
        raise NotImplementedError()
