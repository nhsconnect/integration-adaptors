"""This module defines the asynchronous express workflow."""
from typing import Tuple

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from tornado import httpclient
from utilities import timing

from mhs_common import workflow
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_asynchronous

logger = log.IntegrationAdaptorsLogger('ASYNC_EXPRESS_WORKFLOW')


class AsynchronousExpressWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous express messaging pattern."""

    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None):
        self.persistence_store = persistence_store
        self.transmission = transmission
        self.party_key = party_key
        self.queue_adaptor = queue_adaptor

    @timing.time_function
    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        logger.info('0001', 'Entered async express workflow to handle outbound message')
        wdo = wd.create_new_work_description(self.persistence_store, message_id,
                                                           wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED, workflow.ASYNC_EXPRESS)
        await wdo.publish()

        error, http_headers, message = await self._serialize_outbound_message(message_id, correlation_id, interaction_details,
                                                                payload, wdo)
        if error:
            return error

        logger.info('0004', 'About to make outbound request')
        start_time = timing.get_time()
        try:
            url = interaction_details['url']
            response = await self.transmission.make_request(url, http_headers, message)
            end_time = timing.get_time()
        except httpclient.HTTPClientError as e:
            logger.warning('0005', 'Received HTTP error from Spine. {HTTPStatus} {Exception}',
                           {'HTTPStatus': e.code, 'Exception': e})
            self._record_outbound_audit_log(timing.get_time(), start_time,
                                            wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            await wdo.set_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            return 500, 'Error received from Spine'
        except Exception as e:
            logger.warning('0006', 'Error encountered whilst making outbound request. {Exception}', {'Exception': e})
            await wdo.set_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error making outbound request'

        if response.code == 202:
            self._record_outbound_audit_log(end_time, start_time, wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
            await wdo.set_status(wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
            return 202, ''
        else:
            logger.warning('0008', "Didn't get expected HTTP status 202 from Spine, got {HTTPStatus} instead",
                           {'HTTPStatus': response.code})
            self._record_outbound_audit_log(end_time, start_time, wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            await wdo.set_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            return 500, "Didn't get expected success response from Spine"

    def _record_outbound_audit_log(self, end_time, start_time, acknowledgment):
        logger.audit('0007', 'Async-express workflow invoked. Message sent to Spine and {Acknowledgment} received. '
                             '{RequestSentTime} {AcknowledgmentReceivedTime}',
                     {'RequestSentTime': start_time, 'AcknowledgmentReceivedTime': end_time,
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

    @timing.time_function
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('0009', 'Entered async express workflow to handle inbound message')
        await work_description.set_status(wd.MessageStatus.INBOUND_RESPONSE_RECEIVED)
        try:
            await self.queue_adaptor.send_async(payload, properties={'message-id': message_id,
                                                                     'correlation-id': correlation_id})
        except Exception as e:
            logger.warning('0010', 'Failed to put message onto inbound queue due to {Exception}', {'Exception': e})
            await work_description.set_status(wd.MessageStatus.INBOUND_RESPONSE_FAILED)
            raise e

        logger.info('0011', 'Placed message onto inbound queue successfully')
        await work_description.set_status(wd.MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)
