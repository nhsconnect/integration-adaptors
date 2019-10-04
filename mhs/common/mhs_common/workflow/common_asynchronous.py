"""This module defines the common base for all asynchronous workflows."""
import asyncio
from typing import Dict, Callable, Tuple, Optional

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from exceptions import MaxRetriesExceeded
from tornado import httpclient
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
                 max_request_size: int = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):

        self.persistence_store = persistence_store
        self.transmission = transmission
        self.party_key = party_key
        self.queue_adaptor = queue_adaptor
        self.store_retries = persistence_store_max_retries
        self.inbound_queue_max_retries = inbound_queue_max_retries
        self.inbound_queue_retry_delay = inbound_queue_retry_delay / 1000 if inbound_queue_retry_delay else None
        self.max_request_size = max_request_size
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
            logger.error('0009', 'Failed to serialise outbound message. {Exception}', {'Exception': e})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return (500, 'Error serialising outbound message'), None, None

        if len(message) > self.max_request_size:
            logger.error('0007', 'Request to send to Spine is too large after serialisation. '
                                 '{RequestSize} {MaxRequestSize}',
                         {'RequestSize': len(message), 'MaxRequestSize': self.max_request_size})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return (400, f'Request to send to Spine is too large. MaxRequestSize={self.max_request_size} '
                         f'RequestSize={len(message)}'), None, None

        logger.info('0008', 'Message serialised successfully')
        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED)
        return None, http_headers, message

    async def _make_outbound_request_and_handle_response(
            self, url: str, http_headers: Dict[str, str], message: str, wdo: wd.WorkDescription,
            handle_error_response: Callable[[httpclient.HTTPResponse], Tuple[int, str, Optional[wd.WorkDescription]]]):

        logger.info('0006', 'About to make outbound request')
        try:
            response = await self.transmission.make_request(url, http_headers, message, raise_error_response=False)
        except Exception as e:
            logger.error('0011', 'Error encountered whilst making outbound request. {Exception}', {'Exception': e})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error making outbound request', None

        if response.code == 202:
            logger.audit('0101', '{WorkflowName} outbound workflow invoked. Message sent to Spine and {Acknowledgment} '
                                 'received.',
                         {'Acknowledgment': wd.MessageStatus.OUTBOUND_MESSAGE_ACKD, 'WorkflowName': self.workflow_name})

            await wd.update_status_with_retries(wdo, wdo.set_outbound_status,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                                                self.store_retries)
            return response.code, '', None

        error_response = handle_error_response(response)
        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
        return error_response

    @timing.time_function
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('0010', 'Entered {WorkflowName} workflow to handle inbound message',
                    {'WorkflowName': self.workflow_name})
        logger.audit('0103', '{WorkflowName} inbound workflow invoked. Message received from spine',
                     {'WorkflowName': self.workflow_name})
        await wd.update_status_with_retries(work_description,
                                            work_description.set_inbound_status,
                                            wd.MessageStatus.INBOUND_RESPONSE_RECEIVED,
                                            self.store_retries)

        await self._publish_message_to_inbound_queue(message_id, correlation_id, work_description, payload)

        logger.info('0015', 'Placed message onto inbound queue successfully')
        await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)
        logger.audit('0104', '{WorkflowName} inbound workflow completed. Message placed on queue, returning '
                             '{Acknowledgement} to spine',
                     {'Acknowledgement': wd.MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED,
                      'WorkflowName': self.workflow_name})

    async def _publish_message_to_inbound_queue(self,
                                                message_id: str,
                                                correlation_id: str,
                                                work_description: wd.WorkDescription,
                                                payload: str):
        for retry_num in range(self.inbound_queue_max_retries + 1):
            try:
                await self._put_message_onto_queue_with(message_id, correlation_id, payload)
                break
            except Exception as e:
                logger.warning('0012', 'Failed to put message onto inbound queue due to {Exception}', {'Exception': e})
                if retry_num >= self.inbound_queue_max_retries:
                    logger.error("0013",
                                 "Exceeded the maximum number of retries, {max_retries} retries, when putting "
                                 "message onto inbound queue", {"max_retries": self.inbound_queue_max_retries})
                    await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_FAILED)
                    raise MaxRetriesExceeded('The max number of retries to put a message onto the inbound queue has '
                                             'been exceeded') from e

                logger.info("0014", "Waiting for {retry_delay} seconds before retrying putting message onto inbound "
                                    "queue", {"retry_delay": self.inbound_queue_retry_delay})
                await asyncio.sleep(self.inbound_queue_retry_delay)

    async def _lookup_reliability_details(self, interaction_details: Dict, org_code: str = None) -> Dict:
        try:
            service_id = await self._build_service_id(interaction_details)

            logger.info('0001', 'Looking up reliability details for {service_id}.', {'service_id': service_id})
            reliability_details = await self.routing_reliability.get_reliability(service_id, org_code)

            logger.info('0004', 'Retrieved reliability details for {service_id}. {reliability_details}',
                        {'service_id': service_id, 'reliability_details': reliability_details})
            return reliability_details
        except Exception as e:
            logger.warning('0005', 'Error encountered whilst obtaining outbound URL. {exception}', {'exception': e})
            raise e

    async def _put_message_onto_queue_with(self, message_id, correlation_id, payload, attachments=None):
        await self.queue_adaptor.send_async({'payload': payload, 'attachments': attachments or []},
                                            properties={'message-id': message_id,
                                                        'correlation-id': correlation_id})

    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        pass

    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        pass
