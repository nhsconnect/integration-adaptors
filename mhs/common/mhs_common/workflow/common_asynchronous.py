"""This module defines the common base for all asynchronous workflows."""
from comms import queue_adaptor
from mhs_common.state import persistence_adaptor
from mhs_common.transmission import transmission_adaptor
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import work_description as wd
from mhs_common.workflow.common import CommonWorkflow
from typing import Dict

import utilities.integration_adaptors_logger as log
from mhs_common.routing import routing_reliability

logger = log.IntegrationAdaptorsLogger('COMMON_ASYNC_WORKFLOW')

MHS_SYNC_REPLY_MODE = "nhsMHSSyncReplyMode"
MHS_RETRY_INTERVAL = "nhsMHSRetryInterval"
MHS_RETRIES = "nhsMHSRetries"
MHS_PERSIST_DURATION = "nhsMHSPersistDuration"
MHS_DUPLICATE_ELIMINATION = "nhsMHSDuplicateElimination"
MHS_ACK_REQUESTED = "nhsMHSAckRequested"


class CommonAsynchronousWorkflow(CommonWorkflow):
    """Common functionality across all asynchronous workflows."""
    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 inbound_queue_max_retries: int = None,
                 inbound_queue_retry_delay: int = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):

        self.persistence_store = persistence_store
        self.transmission = transmission
        self.party_key = party_key
        self.queue_adaptor = queue_adaptor
        self.store_retries = persistence_store_max_retries
        self.inbound_queue_max_retries = inbound_queue_max_retries
        self.inbound_queue_retry_delay = inbound_queue_retry_delay / 1000 if inbound_queue_retry_delay else None
        super().__init__(routing)

    async def _serialize_outbound_message(self, message_id, correlation_id, interaction_details, payload, wdo,
                                          to_party_key, cpa_id):
        try:
            interaction_details[ebxml_envelope.MESSAGE_ID] = message_id
            interaction_details[ebxml_request_envelope.MESSAGE] = payload
            interaction_details[ebxml_envelope.FROM_PARTY_ID] = self.party_key
            interaction_details[ebxml_envelope.CONVERSATION_ID] = correlation_id
            interaction_details[ebxml_envelope.TO_PARTY_ID] = to_party_key
            interaction_details[ebxml_envelope.CPA_ID] = cpa_id
            _, http_headers, message = ebxml_request_envelope.EbxmlRequestEnvelope(interaction_details).serialize()
        except Exception as e:
            logger.warning('0002', 'Failed to serialise outbound message. {Exception}', {'Exception': e})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return (500, 'Error serialising outbound message'), None, None

        logger.info('0003', 'Message serialised successfully')
        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED)
        return None, http_headers, message

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
