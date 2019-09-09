"""This module defines the asynchronous express workflow."""
import asyncio
from typing import Dict, List
from typing import Tuple, Optional

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from exceptions import MaxRetriesExceeded
from tornado import httpclient
from utilities import config
from utilities import timing

from mhs_common import workflow
from mhs_common.errors.soap_handler import handle_soap_error
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.routing import routing_reliability
from mhs_common.state import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_asynchronous

ORG_CODE_CONFIG_KEY = "SPINE_ORG_CODE"
MHS_END_POINT_KEY = 'nhsMHSEndPoint'
MHS_TO_PARTY_KEY_KEY = 'nhsMHSPartyKey'
MHS_CPA_ID_KEY = 'nhsMhsCPAId'

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
        self.persistence_store = persistence_store
        self.transmission = transmission
        self.party_key = party_key
        self.queue_adaptor = queue_adaptor
        self.store_retries = persistence_store_max_retries
        self.inbound_queue_max_retries = inbound_queue_max_retries
        self.inbound_queue_retry_delay = inbound_queue_retry_delay / 1000 if inbound_queue_retry_delay else None
        self.routing_reliability = routing

    @timing.time_function
    async def handle_outbound_message(self,
                                      message_id: str,
                                      correlation_id: str,
                                      interaction_details: dict,
                                      payload: str,
                                      wdo: Optional[wd.WorkDescription]) -> Tuple[int, str]:

        logger.info('0001', 'Entered async express workflow to handle outbound message')
        if not wdo:
            wdo = wd.create_new_work_description(self.persistence_store,
                                                 message_id,
                                                 workflow.ASYNC_EXPRESS,
                                                 wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED
                                                 )
            await wdo.publish()

        try:
            url, to_party_key, cpa_id = await self._lookup_endpoint_details(interaction_details)
        except Exception:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error obtaining outbound URL'

        error, http_headers, message = await self._serialize_outbound_message(message_id, correlation_id,
                                                                              interaction_details,
                                                                              payload, wdo, to_party_key, cpa_id)
        if error:
            return error

        logger.info('0004', 'About to make outbound request')
        start_time = timing.get_time()
        try:
            response = await self.transmission.make_request(url, http_headers, message)
            end_time = timing.get_time()
        except httpclient.HTTPClientError as e:
            logger.warning('0005', 'Received HTTP errors from Spine. {HTTPStatus} {Exception}',
                           {'HTTPStatus': e.code, 'Exception': e})
            self._record_outbound_audit_log(timing.get_time(), start_time,
                                            wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)

            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)

            if e.response:
                return handle_soap_error(e.response.code, e.response.headers, e.response.body)

            return 500, f'Error(s) received from Spine: {e}'
        except Exception as e:
            logger.warning('0006', 'Error encountered whilst making outbound request. {Exception}', {'Exception': e})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error making outbound request'

        if response.code == 202:
            self._record_outbound_audit_log(end_time, start_time, wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
            await wd.update_status_with_retries(wdo, wdo.set_outbound_status, wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                                                self.store_retries)
            return 202, ''
        else:
            logger.warning('0008', "Didn't get expected HTTP status 202 from Spine, got {HTTPStatus} instead",
                           {'HTTPStatus': response.code})
            self._record_outbound_audit_log(end_time, start_time, wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            return 500, "Didn't get expected success response from Spine"

    def _record_outbound_audit_log(self, end_time, start_time, acknowledgment):
        logger.audit('0007', 'Async-express workflow invoked. Message sent to Spine and {Acknowledgment} received. '
                             '{RequestSentTime} {AcknowledgmentReceivedTime}',
                     {'RequestSentTime': start_time, 'AcknowledgmentReceivedTime': end_time,
                      'Acknowledgment': acknowledgment})

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

        logger.info('0003', 'Message serialised successfully')
        await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARED)
        return None, http_headers, message

    async def _lookup_endpoint_details(self, interaction_details: Dict) -> Tuple[str, str, str]:
        try:
            service = interaction_details[ebxml_envelope.SERVICE]
            action = interaction_details[ebxml_envelope.ACTION]
            service_id = service + ":" + action
            org_code = config.get_config(ORG_CODE_CONFIG_KEY)

            logger.info('0012', 'Looking up endpoint details for {org_code} & {service_id}.',
                        {'org_code': org_code, 'service_id': service_id})
            endpoint_details = await self.routing_reliability.get_end_point(org_code, service_id)

            url = AsynchronousExpressWorkflow._extract_endpoint_url(endpoint_details)
            to_party_key = endpoint_details[MHS_TO_PARTY_KEY_KEY]
            cpa_id = endpoint_details[MHS_CPA_ID_KEY]
            logger.info('0013', 'Retrieved endpoint details for {org_code} & {service_id}. {url}, {to_party_key}, '
                                '{cpa_id}',
                        {'org_code': org_code, 'service_id': service_id, 'url': url, 'to_party_key': to_party_key,
                         'cpa_id': cpa_id})
            return url, to_party_key, cpa_id
        except Exception as e:
            logger.warning('0014', 'Error encountered whilst obtaining outbound URL. {Exception}', {'Exception': e})
            raise e

    @staticmethod
    def _extract_endpoint_url(endpoint_details: Dict[str, List[str]]) -> str:
        endpoint_urls = endpoint_details[MHS_END_POINT_KEY]

        if len(endpoint_urls) == 0:
            logger.error('0015', 'Did not receive any endpoint URLs when looking up endpoint details.')
            raise IndexError("Did not receive any endpoint URLs when looking up endpoint details.")

        url = endpoint_urls[0]

        if len(endpoint_urls) > 1:
            logger.warning('0016', 'Received more than one URL when looking up endpoint details. Using {url}. '
                                   '{urls_received}', {'url': url, 'urls_received': endpoint_urls})

        return url

    @timing.time_function
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('0009', 'Entered async express workflow to handle inbound message')
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
                logger.warning('0010', 'Failed to put message onto inbound queue due to {Exception}', {'Exception': e})
                retries_remaining -= 1
                if retries_remaining <= 0:
                    logger.warning("0012",
                                   "Exceeded the maximum number of retries, {max_retries} retries, when putting "
                                   "message onto inbound queue", {"max_retries": self.inbound_queue_max_retries})
                    await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_FAILED)
                    raise MaxRetriesExceeded('The max number of retries to put a message onto the inbound queue has '
                                             'been exceeded') from e

                logger.info("0013", "Waiting for {retry_delay} seconds before retrying putting message onto inbound "
                                    "queue", {"retry_delay": self.inbound_queue_retry_delay})
                await asyncio.sleep(self.inbound_queue_retry_delay)

        logger.info('0011', 'Placed message onto inbound queue successfully')
        await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)
