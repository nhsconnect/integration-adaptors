"""This module defines the asynchronous express workflow."""
from typing import Tuple, Optional
from xml.etree import ElementTree as ET

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from tornado import httpclient
from utilities import timing

from mhs_common import workflow
from mhs_common.errors import ebxml_handler
from mhs_common.errors.soap_handler import handle_soap_error
from mhs_common.messages.ebxml_error_envelope import EbxmlErrorEnvelope
from mhs_common.messages.soap_fault_envelope import SOAPFault
from mhs_common.routing import routing_reliability
from persistence import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_asynchronous

logger = log.IntegrationAdaptorsLogger(__name__)


class AsynchronousExpressWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous express messaging pattern."""

    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 max_request_size: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        super().__init__(party_key, persistence_store, transmission, queue_adaptor, max_request_size, routing)

        self.workflow_specific_interaction_details = dict(duplicate_elimination=False,
                                                          ack_requested=False,
                                                          ack_soap_actor="urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
                                                          sync_reply=True)
        self.workflow_name = workflow.ASYNC_EXPRESS

    @timing.time_function
    async def handle_outbound_message(self,
                                      from_asid: Optional[str],
                                      message_id: str,
                                      correlation_id: str,
                                      interaction_details: dict,
                                      payload: str,
                                      wdo: Optional[wd.WorkDescription]) \
            -> Tuple[int, str, Optional[wd.WorkDescription]]:

        logger.info('Entered async express workflow to handle outbound message')
        logger.audit('{WorkflowName} outbound workflow invoked.', fparams={'WorkflowName': self.workflow_name})
        wdo = await self._create_new_work_description_if_required(message_id, wdo, self.workflow_name)

        try:
            details = await self._lookup_endpoint_details(interaction_details)
            url = details[self.ENDPOINT_URL]
            to_party_key = details[self.ENDPOINT_PARTY_KEY]
            cpa_id = details[self.ENDPOINT_CPA_ID]
        except Exception:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Error obtaining outbound URL', None

        error, http_headers, message = await self._serialize_outbound_message(message_id, correlation_id,
                                                                              interaction_details,
                                                                              payload, wdo, to_party_key, cpa_id)
        if error:
            return error[0], error[1], None

        return await self._make_outbound_request_and_handle_response(url, http_headers, message, wdo,
                                                                     self._handle_error_response)

    def _handle_error_response(self, response: httpclient.HTTPResponse):
        try:
            parsed_body = ET.fromstring(response.body)

            if EbxmlErrorEnvelope.is_ebxml_error(parsed_body):
                _, parsed_response = ebxml_handler.handle_ebxml_error(response.code,
                                                                      response.headers,
                                                                      response.body)
                logger.warning('Received ebxml errors from Spine. {HTTPStatus} {Errors}',
                               fparams={'HTTPStatus': response.code, 'Errors': parsed_response})
            elif SOAPFault.is_soap_fault(parsed_body):
                _, parsed_response, _ = handle_soap_error(response.code,
                                                          response.headers,
                                                          response.body)
                logger.warning('Received soap errors from Spine. {HTTPStatus} {Errors}',
                               fparams={'HTTPStatus': response.code, 'Errors': parsed_response})
            else:
                logger.warning("Received an unexpected response from Spine",
                               fparams={'HTTPStatus': response.code})
                parsed_response = "Didn't get expected response from Spine"

        except ET.ParseError:
            logger.exception('Unable to parse response from Spine.')
            parsed_response = 'Unable to handle response returned from Spine'

        return 500, parsed_response, None
