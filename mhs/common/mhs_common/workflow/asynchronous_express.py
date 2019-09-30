"""This module defines the asynchronous express workflow."""
from typing import Tuple, Optional
from xml.etree import ElementTree as ET

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from utilities import timing

from mhs_common import workflow
from mhs_common.errors import ebxml_handler
from mhs_common.errors.soap_handler import handle_soap_error
from mhs_common.messages.ebxml_error_envelope import EbxmlErrorEnvelope
from mhs_common.messages.soap_fault_envelope import SOAPFault
from mhs_common.routing import routing_reliability
from mhs_common.state import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_asynchronous

logger = log.IntegrationAdaptorsLogger('ASYNC_EXPRESS_WORKFLOW')


class AsynchronousExpressWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous express messaging pattern."""

    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 inbound_queue_max_retries: int = None,
                 inbound_queue_retry_delay: int = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        super().__init__(party_key, persistence_store, transmission,
                                                          queue_adaptor, inbound_queue_max_retries,
                                                          inbound_queue_retry_delay, persistence_store_max_retries,
                                                          routing)

        self.workflow_specific_interaction_details = dict(duplicate_elimination=False,
                                                          ack_requested=False,
                                                          ack_soap_actor="urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
                                                          sync_reply=True)

    @timing.time_function
    async def handle_outbound_message(self,
                                      from_asid: Optional[str],
                                      message_id: str,
                                      correlation_id: str,
                                      interaction_details: dict,
                                      payload: str,
                                      wdo: Optional[wd.WorkDescription])\
            -> Tuple[int, str, Optional[wd.WorkDescription]]:

        logger.info('0001', 'Entered async express workflow to handle outbound message')
        if not wdo:
            wdo = wd.create_new_work_description(self.persistence_store,
                                                 message_id,
                                                 workflow.ASYNC_EXPRESS,
                                                 outbound_status=wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED
                                                 )
            await wdo.publish()

        try:
            details = await self._lookup_endpoint_details(interaction_details)
            url = details[self.ENDPOINT_URL]
            to_party_key = details[self.ENDPOINT_PARTY_KEY]
            cpa_id = details[self.ENDPOINT_CPA_ID]
        except Exception:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error obtaining outbound URL', None

        error, http_headers, message = await self._serialize_outbound_message(message_id, correlation_id,
                                                                              interaction_details,
                                                                              payload, wdo, to_party_key, cpa_id)
        if error:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return error[0], error[1], None

        start_time = timing.get_time()
        logger.info('0004', 'About to make outbound request')
        response = await self.transmission.make_request(url, http_headers, message, raise_error_response=False)

        if response.code == 202:
            end_time = timing.get_time()
            self._record_outbound_audit_log(workflow.ASYNC_EXPRESS, end_time, start_time,
                                            wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
            await wd.update_status_with_retries(wdo, wdo.set_outbound_status,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                                                self.store_retries)
            return response.code, '', None
        else:
            try:
                parsed_body = ET.fromstring(response.body)

                if EbxmlErrorEnvelope.is_ebxml_error(parsed_body):
                    _, parsed_response = ebxml_handler.handle_ebxml_error(response.code,
                                                                          response.headers,
                                                                          response.body)
                    logger.warning('0007', 'Received ebxml errors from Spine. {HTTPStatus} {Errors}',
                                   {'HTTPStatus': response.code, 'Errors': parsed_response})
                elif SOAPFault.is_soap_fault(parsed_body):
                    _, parsed_response, _ = handle_soap_error(response.code,
                                                              response.headers,
                                                              response.body)
                    logger.warning('0008', 'Received soap errors from Spine. {HTTPStatus} {Errors}',
                                   {'HTTPStatus': response.code, 'Errors': parsed_response})
                else:
                    logger.warning('0009', "Received an unexpected response from Spine",
                                   {'HTTPStatus': response.code})
                    parsed_response = "Didn't get expected response from Spine"

                self._record_outbound_audit_log(workflow.ASYNC_EXPRESS, timing.get_time(), start_time,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
                await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            except ET.ParseError as pe:
                logger.warning('0010', 'Unable to parse response from Spine. {Exception}', {'Exception': repr(pe)})
                parsed_response = 'Unable to handle response returned from Spine'

            return 500, parsed_response, None

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('0010', 'Entered async express workflow to handle inbound message')
        await super()._handle_inbound_message(message_id, correlation_id, work_description, payload)
