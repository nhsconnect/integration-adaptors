"""This module defines the asynchronous reliable workflow."""
import asyncio
import functools
from typing import Tuple, Optional, List, Dict
from xml.etree import ElementTree as ET

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from isodate import isoerror
from tornado import httpclient
from utilities import timing
from utilities.date_utilities import DateUtilities

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


class AsynchronousReliableWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous reliable messaging pattern."""

    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 max_request_size: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        super().__init__(party_key, persistence_store, transmission, queue_adaptor, max_request_size, routing)

        self.workflow_specific_interaction_details = dict(duplicate_elimination=True,
                                                          ack_requested=True,
                                                          ack_soap_actor="urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
                                                          sync_reply=True)
        self.workflow_name = workflow.ASYNC_RELIABLE

    @timing.time_function
    async def handle_outbound_message(self, from_asid: Optional[str],
                                      message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      wdo: Optional[wd.WorkDescription]) \
            -> Tuple[int, str, Optional[wd.WorkDescription]]:

        logger.info('Entered async reliable workflow to handle outbound message')
        wdo = await self._create_new_work_description_if_required(message_id, wdo, self.workflow_name)
        logger.audit('Outbound {WorkflowName} workflow invoked.', fparams={'WorkflowName': self.workflow_name})

        try:
            details = await self._lookup_endpoint_details(interaction_details)
            url = details[self.ENDPOINT_URL]
            to_party_key = details[self.ENDPOINT_PARTY_KEY]
            cpa_id = details[self.ENDPOINT_CPA_ID]
        except Exception:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Error obtaining outbound URL', None

        reliability_details = await self._lookup_reliability_details(interaction_details)
        retry_interval_xml_datetime = reliability_details[common_asynchronous.MHS_RETRY_INTERVAL]
        try:
            retry_interval = DateUtilities.convert_xml_date_time_format_to_seconds(retry_interval_xml_datetime)
        except isoerror.ISO8601Error:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Error when converting retry interval: {} to seconds'.format(retry_interval_xml_datetime), None

        error, http_headers, message = await self._serialize_outbound_message(message_id, correlation_id,
                                                                              interaction_details,
                                                                              payload, wdo, to_party_key, cpa_id)
        if error:
            return error[0], error[1], None

        return await self._make_outbound_request_with_retries_and_handle_response(url, http_headers, message, wdo,
                                                                                  reliability_details, retry_interval)

    async def _make_outbound_request_with_retries_and_handle_response(self, url: str, http_headers: Dict[str, str],
                                                                      message: str, wdo: wd.WorkDescription,
                                                                      reliability_details: dict, retry_interval: float):
        num_of_retries = int(reliability_details[common_asynchronous.MHS_RETRIES])

        # retries_remaining is a mutable integer. This is done by putting an (immutable) integer into
        # a mutable container.
        retries_remaining = [num_of_retries]

        handle_error_response = functools.partial(self._handle_error_response,
                                                  num_of_retries=num_of_retries, retries_remaining=retries_remaining)

        while True:
            try:
                return await self._make_outbound_request_and_handle_response(url, http_headers, message, wdo,
                                                                             handle_error_response)
            except _NeedToRetryException:
                retries_remaining[0] -= 1
                logger.info("Waiting for {retry_interval} seconds before next request attempt.",
                            fparams={"retry_interval": retry_interval})
                await asyncio.sleep(retry_interval)
                continue

    def _handle_error_response(self, response: httpclient.HTTPResponse, num_of_retries: int,
                               retries_remaining: List[int]):
        try:
            parsed_body = ET.fromstring(response.body)

            if EbxmlErrorEnvelope.is_ebxml_error(parsed_body):
                _, parsed_response = ebxml_handler.handle_ebxml_error(response.code,
                                                                      response.headers,
                                                                      response.body)
                logger.warning('Received ebxml errors from Spine. {HTTPStatus} {Errors}',
                               fparams={'HTTPStatus': response.code, 'Errors': parsed_response})

            elif SOAPFault.is_soap_fault(parsed_body):
                _, parsed_response, soap_fault_codes = handle_soap_error(response.code,
                                                                         response.headers,
                                                                         response.body)
                logger.warning('Received soap errors from Spine. {HTTPStatus} {Errors}',
                               fparams={'HTTPStatus': response.code, 'Errors': parsed_response})

                if SOAPFault.is_soap_fault_retriable(soap_fault_codes):
                    logger.warning("A retriable error was encountered {error} {retries_remaining} {max_retries}",
                                   fparams={
                                       "error": parsed_response,
                                       "retries_remaining": retries_remaining[0],
                                       "max_retries": num_of_retries
                                   })
                    if retries_remaining[0] <= 0:
                        # exceeded the number of retries so return the SOAP error response
                        logger.error("A request has exceeded the maximum number of retries, {max_retries} retries",
                                     fparams={"max_retries": num_of_retries})
                    else:
                        raise _NeedToRetryException()
            else:
                logger.warning("Received an unexpected response from Spine", fparams={'HTTPStatus': response.code})
                parsed_response = "Didn't get expected response from Spine"

        except ET.ParseError:
            logger.exception('Unable to parse response from Spine.')
            parsed_response = 'Unable to handle response returned from Spine'

        return 500, parsed_response, None


class _NeedToRetryException(Exception):
    pass
