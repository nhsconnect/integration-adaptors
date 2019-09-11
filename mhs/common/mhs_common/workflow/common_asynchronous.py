"""This module defines the common base for all asynchronous workflows."""
from typing import Dict

import utilities.integration_adaptors_logger as log

import mhs_common.workflow.common as common

logger = log.IntegrationAdaptorsLogger('COMMON_ASYNC_WORKFLOW')

MHS_SYNC_REPLY_MODE = "nhsMHSSyncReplyMode"
MHS_RETRY_INTERVAL = "nhsMHSRetryInterval"
MHS_RETRIES = "nhsMHSRetries"
MHS_PERSIST_DURATION = "nhsMHSPersistDuration"
MHS_DUPLICATE_ELIMINATION = "nhsMHSDuplicateElimination"
MHS_ACK_REQUESTED = "nhsMHSAckRequested"


class CommonAsynchronousWorkflow(common.CommonWorkflow):
    """Common functionality across all asynchronous workflows."""

    async def _lookup_reliability_details(self, interaction_details: Dict) -> Dict:
        try:
            service_id = await self._build_service_id(interaction_details)

            logger.info('0001', 'Looking up reliability details for {service_id}.', {'service_id': service_id})
            reliability_details = await self.routing_reliability.get_reliability(service_id)

            logger.info('0002', 'Retrieved reliability details for {service_id}. {reliability_details}',
                        {'service_id': service_id, 'reliability_details': reliability_details})
            return reliability_details
        except Exception as e:
            logger.warning('0003', 'Error encountered whilst obtaining outbound URL. {exception}', {'exception': e})
            raise e
