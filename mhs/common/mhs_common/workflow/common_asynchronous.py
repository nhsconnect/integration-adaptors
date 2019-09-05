"""This module defines the common base for all asynchronous workflows."""
from comms import queue_adaptor
from mhs_common.state import persistence_adaptor
from mhs_common.transmission import transmission_adaptor
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import work_description as wd
from  mhs_common.workflow.common import CommonWorkflow
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('COMMON_ASYNC_WORKFLOW')


class CommonAsynchronousWorkflow(CommonWorkflow):
    """Common functionality across all asynchronous workflows."""
    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 inbound_queue_max_retries: int = None,
                 inbound_queue_retry_delay: int = None):

        self.persistence_store = persistence_store
        self.transmission = transmission
        self.party_key = party_key
        self.queue_adaptor = queue_adaptor
        self.inbound_queue_max_retries = inbound_queue_max_retries
        self.inbound_queue_retry_delay = inbound_queue_retry_delay / 1000 if inbound_queue_retry_delay else None

    def _record_outbound_audit_log(self, workflow, end_time, start_time, acknowledgment):
        logger.audit('0007', '{workflow} workflow invoked. Message sent to Spine and {Acknowledgment} received. '
                             '{RequestSentTime} {AcknowledgmentReceivedTime}', {'workflow': workflow,
                                                                                'RequestSentTime': start_time,
                                                                                'AcknowledgmentReceivedTime': end_time,
                                                                                'Acknowledgment': acknowledgment})

    async def _serialize_outbound_message(self, message_id, correlation_id, interaction_details, payload, wdo):
        try:
            interaction_details[ebxml_envelope.MESSAGE_ID] = message_id
            interaction_details[ebxml_request_envelope.MESSAGE] = payload
            interaction_details[ebxml_envelope.FROM_PARTY_ID] = self.party_key
            interaction_details[ebxml_envelope.CONVERSATION_ID] = correlation_id
            _, http_headers, message = ebxml_request_envelope.EbxmlRequestEnvelope(interaction_details).serialize()
        except Exception as e:
            logger.warning('0002', 'Failed to serialise outbound message. {Exception}', {'Exception': e})
            await wdo.set_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return (500, 'Error serialising outbound message'), None, None

        logger.info('0003', 'Message serialised successfully')
        await wdo.set_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED)
        return None, http_headers, message

