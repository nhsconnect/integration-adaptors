"""This module defines the common base for all asynchronous workflows."""
import asyncio
from typing import Dict

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from exceptions import MaxRetriesExceeded
from utilities import timing

from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.routing import routing_reliability
from mhs_common.state import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow.common import CommonWorkflow

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

    async def _create_new_work_description_if_required(self, message_id: str, wdo: wd.WorkDescription,
                                                       workflow_name: str):
        if not wdo:
            wdo = wd.create_new_work_description(self.persistence_store,
                                                 message_id,
                                                 workflow_name,
                                                 outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED
                                                 )
            await wdo.publish()
        return wdo

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

    @timing.time_function
    async def _handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        await wd.update_status_with_retries(work_description,
                                            work_description.set_inbound_status,
                                            wd.MessageStatus.INBOUND_RESPONSE_RECEIVED,
                                            self.store_retries)

        retries_remaining = self.inbound_queue_max_retries
        while True:
            try:
                await self._put_message_onto_queue_with(message_id, correlation_id, payload)
                break
            except Exception as e:
                logger.warning('0012', 'Failed to put message onto inbound queue due to {Exception}', {'Exception': e})
                retries_remaining -= 1
                if retries_remaining <= 0:
                    logger.error("0013",
                                 "Exceeded the maximum number of retries, {max_retries} retries, when putting "
                                 "message onto inbound queue", {"max_retries": self.inbound_queue_max_retries})
                    await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_FAILED)
                    raise MaxRetriesExceeded('The max number of retries to put a message onto the inbound queue has '
                                             'been exceeded') from e

                logger.info("0014", "Waiting for {retry_delay} seconds before retrying putting message onto inbound "
                                    "queue", {"retry_delay": self.inbound_queue_retry_delay})
                await asyncio.sleep(self.inbound_queue_retry_delay)

        logger.info('0015', 'Placed message onto inbound queue successfully')
        await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)

    async def _lookup_reliability_details(self, interaction_details: Dict, org_code: str = None) -> Dict:
        try:
            service_id = await self._build_service_id(interaction_details)

            logger.info('0001', 'Looking up reliability details for {service_id}.', {'service_id': service_id})
            reliability_details = await self.routing_reliability.get_reliability(service_id, org_code)

            logger.info('0002', 'Retrieved reliability details for {service_id}. {reliability_details}',
                        {'service_id': service_id, 'reliability_details': reliability_details})
            return reliability_details
        except Exception as e:
            logger.warning('0003', 'Error encountered whilst obtaining outbound URL. {exception}', {'exception': e})
            raise e

    async def _put_message_onto_queue_with(self, message_id, correlation_id, payload, attachments=None):
        await self.queue_adaptor.send_async({'payload': payload, 'attachments': attachments or []},
                                            properties={'message-id': message_id,
                                                        'correlation-id': correlation_id})

    def _record_outbound_audit_log(self, workflow_name: str, end_time: str, start_time: str,
                                   acknowledgment: wd.MessageStatus):
        logger.audit('0011', '{WorkflowName} invoked. Message sent to Spine and {Acknowledgment} received. '
                             '{RequestSentTime} {AcknowledgmentReceivedTime}',
                     {'WorkflowName': workflow_name, 'RequestSentTime': start_time, 'AcknowledgmentReceivedTime': end_time,
                      'Acknowledgment': acknowledgment})

    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        pass

    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        pass
