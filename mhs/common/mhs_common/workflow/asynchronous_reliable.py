"""This module defines the asynchronous express workflow."""
from isodate import isoerror

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from xml.etree import ElementTree as ET
from typing import Tuple, Optional

from mhs_common.messages.ebxml_error_envelope import EbxmlErrorEnvelope
from mhs_common.messages.soap_fault_envelope import SOAPFault
from utilities import timing

from mhs_common import workflow
from mhs_common.errors import ebxml_handler
from mhs_common.errors.soap_handler import handle_soap_error
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_asynchronous
from mhs_common.routing import routing_reliability
from exceptions import MaxRetriesExceeded
import asyncio

from utilities.date_utilities import DateUtilities

logger = log.IntegrationAdaptorsLogger('ASYNC_RELIABLE_WORKFLOW')


class AsynchronousReliableWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous reliable messaging pattern."""

    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 inbound_queue_max_retries: int = None,
                 inbound_queue_retry_delay: int = None,
                 max_request_size: int = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        super(AsynchronousReliableWorkflow, self).__init__(party_key, persistence_store, transmission,
                                                           queue_adaptor, inbound_queue_max_retries,
                                                           inbound_queue_retry_delay, max_request_size,
                                                           persistence_store_max_retries, routing)

        self.workflow_specific_interaction_details = dict(duplicate_elimination=True,
                                                          ack_requested=True,
                                                          ack_soap_actor="urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
                                                          sync_reply=True)

    @timing.time_function
    async def handle_outbound_message(self, from_asid: Optional[str],
                                      message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      wdo: Optional[wd.WorkDescription]) \
            -> Tuple[int, str, Optional[wd.WorkDescription]]:

        logger.info('0001', 'Entered async reliable workflow to handle outbound message')
        logger.audit('0100', 'Outbound Async-Reliable workflow invoked.')
        if not wdo:
            wdo = wd.create_new_work_description(self.persistence_store,
                                                 message_id,
                                                 workflow.ASYNC_RELIABLE,
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

        reliability_details = await self._lookup_reliability_details(interaction_details)
        retry_interval_xml_datetime = reliability_details[common_asynchronous.MHS_RETRY_INTERVAL]
        try:
            retry_interval = DateUtilities.convert_xml_date_time_format_to_seconds(retry_interval_xml_datetime)
        except isoerror.ISO8601Error:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error when converting retry interval: {} to seconds'.format(retry_interval_xml_datetime), None

        num_of_retries = int(reliability_details[common_asynchronous.MHS_RETRIES])

        retries_remaining = num_of_retries

        while True:
            logger.info('0004', 'About to make outbound request')
            response = await self.transmission.make_request(url, http_headers, message, raise_error_response=False)

            if response.code == 202:
                logger.audit('0101',
                             'Outbound Async-Reliable outbound workflow completed. Message sent to Spine'
                             ' and {Acknowledgment} received.',
                             {'Acknowledgment': wd.MessageStatus.OUTBOUND_MESSAGE_ACKD})
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
                        _, parsed_response, soap_fault_codes = handle_soap_error(response.code,
                                                                                 response.headers,
                                                                                 response.body)
                        logger.warning('0008', 'Received soap errors from Spine. {HTTPStatus} {Errors}',
                                       {'HTTPStatus': response.code, 'Errors': parsed_response})

                        if SOAPFault.is_soap_fault_retriable(soap_fault_codes):
                            retries_remaining -= 1
                            logger.warning("0015", "A retriable error was encountered {error} {retries_remaining} "
                                                   "{max_retries}",
                                           {"error": parsed_response,
                                            "retries_remaining": retries_remaining,
                                            "max_retries": num_of_retries})
                            if retries_remaining <= 0:
                                # exceeded the number of retries so return the SOAP error response
                                logger.error("0016",
                                             "A request has exceeded the maximum number of retries, {max_retries} "
                                             "retries", {"max_retries": num_of_retries})
                            else:
                                logger.info("0016", "Waiting for {retry_interval} seconds before next request "
                                                    "attempt.", {"retry_interval": retry_interval})
                                await asyncio.sleep(retry_interval)
                                continue
                    else:
                        logger.warning('0017', "Received an unexpected response from Spine",
                                       {'HTTPStatus': response.code})
                        parsed_response = "Didn't get expected response from Spine"

                    await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
                except ET.ParseError as pe:
                    logger.warning('0010', 'Unable to parse response from Spine. {Exception}',
                                   {'Exception': repr(pe)})
                    parsed_response = 'Unable to handle response returned from Spine'
                    await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)

                return 500, parsed_response, None

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

        if len(message) > self.max_request_size:
            logger.error('0005', 'Request to send to Spine is too large after serialisation. '
                                 '{RequestSize} {MaxRequestSize}',
                         {'RequestSize': len(message), 'MaxRequestSize': self.max_request_size})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return (400, f'Request to send to Spine is too large. MaxRequestSize={self.max_request_size} '
                         f'RequestSize={len(message)}'), None, None

        logger.info('0003', 'Message serialised successfully')
        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED)
        return None, http_headers, message

    @timing.time_function
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('0010', 'Entered async reliable workflow to handle inbound message')
        logger.audit('0103', 'Async-Reliable inbound workflow invoked. Message received from Spine.')

        await wd.update_status_with_retries(work_description,
                                            work_description.set_inbound_status,
                                            wd.MessageStatus.INBOUND_RESPONSE_RECEIVED,
                                            self.store_retries)

        retries_remaining = self.inbound_queue_max_retries
        while True:
            try:
                await self.queue_adaptor.send_async(payload, properties={'message-id': message_id,
                                                                         'correlation-id': correlation_id})
                break
            except Exception as e:
                logger.warning('0011', 'Failed to put message onto inbound queue due to {Exception}', {'Exception': e})
                retries_remaining -= 1
                if retries_remaining <= 0:
                    logger.error("0012",
                                 "Exceeded the maximum number of retries, {max_retries} retries, when putting "
                                 "message onto inbound queue", {"max_retries": self.inbound_queue_max_retries})
                    await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_FAILED)
                    raise MaxRetriesExceeded('The max number of retries to put a message onto the inbound queue has '
                                             'been exceeded') from e

                logger.info("0013", "Waiting for {retry_delay} seconds before retrying putting message onto inbound "
                                    "queue", {"retry_delay": self.inbound_queue_retry_delay})
                await asyncio.sleep(self.inbound_queue_retry_delay)

        logger.info('0014', 'Placed message onto inbound queue successfully')
        await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)
        logger.audit('0104',
                     'Inbound Async-Reliable outbound workflow completed. Message placed on queue, returning '
                     'acknowledgement to spine {Acknowledgement}',
                     {'Acknowledgement': wd.MessageStatus.OUTBOUND_MESSAGE_ACKD})

    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        pass

    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        pass
