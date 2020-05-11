"""This module defines the synchronous workflow."""
from typing import Tuple, Optional
import utilities.integration_adaptors_logger as log
from tornado import httpclient

from mhs_common.workflow.common import MessageData
from utilities import timing
from mhs_common import workflow
from mhs_common.errors.soap_handler import handle_soap_error
from mhs_common.messages import soap_envelope
from persistence import persistence_adaptor as pa
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_synchronous
from mhs_common.routing import routing_reliability

logger = log.IntegrationAdaptorsLogger(__name__)


class SynchronousWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the synchronous messaging pattern."""

    def __init__(self,
                 party_key: str = None,
                 work_description_store: pa.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 max_request_size: int = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        super().__init__(routing)
        self.party_key = party_key
        self.wd_store = work_description_store
        self.transmission = transmission
        self.max_request_size = max_request_size
        self.persistence_store_retries = persistence_store_max_retries
        self.workflow_name = workflow.ASYNC_EXPRESS

    @timing.time_function
    async def handle_outbound_message(self,
                                      from_asid: str,
                                      message_id: str,
                                      correlation_id: str,
                                      interaction_details: dict,
                                      payload: str,
                                      work_description_object: Optional[wd.WorkDescription]) \
            -> Tuple[int, str, Optional[wd.WorkDescription]]:
        logger.info('Entered sync workflow for outbound message')
        logger.audit('Outbound Synchronous workflow invoked.')

        wdo = wd.create_new_work_description(self.wd_store,
                                             message_id,
                                             workflow.SYNC,
                                             outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)
        await wdo.publish()

        if not from_asid:
            return 400, '`from_asid` header field required for sync messages', None

        try:
            endpoint_details = await self._lookup_endpoint_details(interaction_details)
            url = endpoint_details[self.ENDPOINT_URL]
            to_asid = endpoint_details[self.ENDPOINT_TO_ASID]
        except Exception:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Error obtaining outbound URL', None

        try:
            message_id, headers, message = await self._prepare_outbound_message(message_id,
                                                                                to_asid,
                                                                                from_asid=from_asid,
                                                                                interaction_details=interaction_details,
                                                                                message=payload)
        except Exception:
            logger.exception('Failed to prepare outbound message')
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Failed message preparation', None

        if len(message) > self.max_request_size:
            logger.error('Request to send to Spine is too large after serialisation. {RequestSize} {MaxRequestSize}',
                         fparams={'RequestSize': len(message), 'MaxRequestSize': self.max_request_size})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 400, f'Request to send to Spine is too large. MaxRequestSize={self.max_request_size} '\
                        f'RequestSize={len(message)}', None

        logger.info('Outbound message prepared')
        try:
            response = await self.transmission.make_request(url, headers, message)
        except httpclient.HTTPClientError as e:
            code, error = await self._handle_http_exception(e, wdo)
            return code, error, wdo

        except Exception:
            logger.exception('Error encountered whilst making outbound request.')
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error making outbound request', None

        logger.audit('Outbound Synchronous workflow completed. Message sent to Spine and {Acknowledgment} received.',
                     fparams={'Acknowledgment': wd.MessageStatus.OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED})

        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED)
        return response.code, response.body.decode(), wdo

    async def _handle_http_exception(self, exception, wdo):
        logger.exception('Received HTTP errors from Spine. {HTTPStatus}', fparams={'HTTPStatus': exception.code})

        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED)

        if exception.response:
            code, response, _ = handle_soap_error(exception.response.code,
                                                  exception.response.headers,
                                                  exception.response.body)
            return code, response

        return 500, f'Error(s) received from Spine: {exception}'

    async def _prepare_outbound_message(self, message_id: Optional[str], to_asid: str, from_asid: str,
                                        message: str,
                                        interaction_details: dict):
        action = f'{interaction_details[soap_envelope.SERVICE]}/{interaction_details[soap_envelope.ACTION]}'
        message_details = {
            soap_envelope.MESSAGE_ID: message_id,
            soap_envelope.TO_ASID: to_asid,
            soap_envelope.FROM_ASID: from_asid,
            soap_envelope.SERVICE: interaction_details[soap_envelope.SERVICE],
            soap_envelope.ACTION: action,
            soap_envelope.MESSAGE: message
        }

        envelope = soap_envelope.SoapEnvelope(message_details)
        return envelope.serialize()

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription, message_data: MessageData):
        raise NotImplementedError('This method is not supported for the synchronous message workflow as there is no '
                                  'inbound message')

    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        await wdo.set_outbound_status(wd.MessageStatus.SYNC_RESPONSE_SUCCESSFUL)

    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        await wdo.set_outbound_status(wd.MessageStatus.SYNC_RESPONSE_FAILED)
