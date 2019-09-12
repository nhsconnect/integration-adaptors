"""This module defines the synchronous workflow."""
from typing import Tuple, Optional
import utilities.integration_adaptors_logger as log
from tornado import httpclient
from utilities import timing
from mhs_common import workflow
from mhs_common.errors.soap_handler import handle_soap_error
from mhs_common.messages import soap_envelope
from mhs_common.state import persistence_adaptor as pa
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_synchronous
from mhs_common.routing import routing_reliability

logger = log.IntegrationAdaptorsLogger('SYNC_WORKFLOW')


class SynchronousWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the synchronous messaging pattern."""

    def __init__(self,
                 party_key: str = None,
                 work_description_store: pa.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        self.party_key = party_key
        self.wd_store = work_description_store
        self.transmission = transmission
        self.persistence_store_retries = persistence_store_max_retries
        super().__init__(routing)

    async def handle_outbound_message(self,
                                      message_id: str,
                                      correlation_id: str,
                                      interaction_details: dict,
                                      payload: str,
                                      work_description_object: Optional[wd.WorkDescription]) \
            -> Tuple[int, str, Optional[wd.WorkDescription]]:
        logger.info('001', 'Entered sync workflow for outbound message')
        wdo = wd.create_new_work_description(self.wd_store,
                                             message_id,
                                             workflow.SYNC,
                                             wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED
                                             )
        await wdo.publish()

        try:
            url, to_asid = await self._lookup_to_asid_details(interaction_details)
        except Exception:
            logger.error('009', 'Failed to retrieve details from spine route lookup')
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Error obtaining outbound URL', None

        try:
            message_id, headers, message = await self._prepare_outbound_message(message_id,
                                                                                to_asid,
                                                                                from_asid="918999199084",
                                                                                interaction_details=interaction_details,
                                                                                message=payload)
        except Exception:
            logger.error('002', 'Failed to prepare outbound message')
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Failed message preparation', None

        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED)

        logger.info('003', 'About to make outbound request')
        start_time = timing.get_time()
        try:
            response = await self.transmission.make_request(url, headers, message)
            end_time = timing.get_time()
        except httpclient.HTTPClientError as e:
            logger.warning('0005', 'Received HTTP errors from Spine. {HTTPStatus} {Exception}',
                           {'HTTPStatus': e.code, 'Exception': e})

            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)

            if e.response:
                code, response = handle_soap_error(e.response.code, e.response.headers, e.response.body)
                return  code, response, None

            return 500, f'Error(s) received from Spine: {e}', None
        except Exception as e:
            logger.warning('0006', 'Error encountered whilst making outbound request. {Exception}', {'Exception': e})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error making outbound request', None

        logger.info('0021', 'Response received from spine {startTime} {endTime}',
                    {'startTime': start_time, 'endTime': end_time})
        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_RESPONSE_RECEIVED)
        return response.code, response.body.decode(), wdo

    async def _prepare_outbound_message(self, message_id: Optional[str], to_asid: str, from_asid: str,
                                        message: str,
                                        interaction_details: dict):

        message_details = {
            soap_envelope.MESSAGE_ID: message_id,
            soap_envelope.TO_ASID: to_asid,
            soap_envelope.FROM_ASID: from_asid,
            soap_envelope.SERVICE: interaction_details[soap_envelope.SERVICE],
            soap_envelope.ACTION: interaction_details[soap_envelope.ACTION],
            soap_envelope.MESSAGE: message
        }

        envelope = soap_envelope.SoapEnvelope(message_details)
        return envelope.serialize()

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        raise NotImplementedError('This method is not supported for the synchronous message workflow as there is no '
                                  'inbound message')
