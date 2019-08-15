"""This module defines the asynchronous express workflow."""
from typing import Tuple

import requests
import utilities.integration_adaptors_logger as log
from comms import transmission_adaptor
from utilities import timing

from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import persistence_adaptor, work_description
from mhs_common.workflow import common_asynchronous

logger = log.IntegrationAdaptorsLogger('ASYNC_EXPRESS_WORKFLOW')


class AsynchronousExpressWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous express messaging pattern."""

    def __init__(self, persistence_store: persistence_adaptor.PersistenceAdaptor,
                 transmission: transmission_adaptor.TransmissionAdaptor, party_key: str):
        self.persistence_store = persistence_store
        self.transmission = transmission
        self.party_key = party_key

    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        logger.info('0001', 'Entered async express workflow to handle outbound message')
        wdo = work_description.create_new_work_description(self.persistence_store, message_id,
                                                           work_description.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)
        await wdo.publish()

        try:
            # Call message packer to serialise message
            interaction_details[ebxml_envelope.MESSAGE_ID] = message_id
            interaction_details[ebxml_request_envelope.MESSAGE] = payload
            interaction_details[ebxml_envelope.FROM_PARTY_ID] = self.party_key
            interaction_details[ebxml_envelope.CONVERSATION_ID] = correlation_id
            _, http_headers, message = ebxml_request_envelope.EbxmlRequestEnvelope(interaction_details).serialize()
        except Exception as e:
            logger.warning('0002', 'Failed to serialise outbound message. {Exception}', {'Exception': e})
            await wdo.set_status(work_description.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Error serialising outbound message'
        else:
            logger.info('0003', 'Message serialised successfully')
            await wdo.set_status(work_description.MessageStatus.OUTBOUND_MESSAGE_PREPARED)

        try:
            logger.info('0004', 'About to make outbound request')
            start_time = timing.get_time()
            response = await self.transmission.make_request(interaction_details, message)
            end_time = timing.get_time()
        except requests.exceptions.HTTPError as e:
            logger.warning('0005', 'Received HTTP error from Spine. {HTTPStatus} {Exception}',
                           {'HTTPStatus': e.response.http_status, 'Exception': e})
            await wdo.set_status(work_description.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            return 500, 'Error received from Spine'
        except Exception as e:
            logger.warning('0006', 'Error encountered whilst making outbound request. {Exception}', {'Exception': e})
            await wdo.set_status(work_description.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error making outbound request'

        if response.status_code == 202:
            logger.audit('0007', 'Async-express workflow invoked. Message sent to Spine and acknowledgment received. '
                                 '{RequestSentTime} {AcknowledgmentReceivedTime}',
                         {'RequestSentTime': start_time, 'AcknowledgmentReceivedTime': end_time})
            await wdo.set_status(work_description.MessageStatus.OUTBOUND_MESSAGE_ACKD)
            return 202, ''
        else:
            logger.warning('0008', "Didn't get expected HTTP status 202 from Spine, got {HTTPStatus} instead",
                           {'HTTPStatus': response.status_code})
            await wdo.set_status(work_description.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            return 500, "Didn't get expected success response from Spine"
