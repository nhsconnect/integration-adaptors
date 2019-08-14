"""This module defines the asynchronous express workflow."""
from typing import Tuple

from mhs_common.state import persistence_adaptor, work_description
from mhs_common.workflow import common_asynchronous


class AsynchronousExpressWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous express messaging pattern."""

    def __init__(self, persistence_store: persistence_adaptor.PersistenceAdaptor):
        self.persistence_store = persistence_store

        raise NotImplementedError()
    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
