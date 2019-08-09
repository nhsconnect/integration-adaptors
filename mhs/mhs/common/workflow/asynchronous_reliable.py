"""This module defines the asynchronous reliable workflow."""
from typing import Tuple

import mhs.common.workflow.common_asynchronous as common_asynchronous


class AsynchronousReliableWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous reliable messaging pattern."""

    async def handle_supplier_message(self, message_id: str, interaction_details: dict, payload: str) \
            -> Tuple[int, str]:
        raise NotImplementedError()
