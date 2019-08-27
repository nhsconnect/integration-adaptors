"""This module defines the sync-async workflow."""

from typing import Tuple

from utilities import integration_adaptors_logger as log

from mhs_common.state import work_description as wd
from mhs_common.workflow import common_synchronous, common_asynchronous

logger = log.IntegrationAdaptorsLogger('MHS_SYNC_ASYNC_WORKFLOW')


ASYNC_RESPONSE_EXPECTED = 'async_response_expected'


class SyncAsyncWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the sync-async messaging pattern."""

    # TODO: This used to take an outbound transmission object
    def __init__(self, workflow: common_asynchronous.CommonAsynchronousWorkflow):

        """Create a new SyncAsyncWorkflow that uses the specified dependencies to load config, build a message and
        send it.
        """
        self.workflow = workflow

    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        return await self.workflow.handle_outbound_message(message_id, correlation_id, interaction_details, payload)
        # TODO-look at return value, if it's an ack, then pause request, else passthrough error
        # TODO-when request resumes, return response it resumed with

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        raise NotImplementedError()
