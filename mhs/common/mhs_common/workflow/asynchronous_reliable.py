"""This module defines the asynchronous reliable workflow."""
from typing import Tuple, Optional

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from tornado import httpclient
from typing import Tuple, Optional

from utilities import timing

from mhs_common import workflow
from mhs_common.errors.soap_handler import handle_soap_error
from mhs_common.state import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_asynchronous
from mhs_common.routing import routing_reliability
from exceptions import MaxRetriesExceeded
import asyncio

logger = log.IntegrationAdaptorsLogger('ASYNC_RELIABLE_WORKFLOW')

SYSTEM_FAILURE_TO_PROCESS_MESSAGE_ERROR_CODE = 200
ROUTING_DELIVERY_FAILURE_ERROR_CODE = 206
FAILURE_STORING_VARIABLE_IN_MEMO = 208

class AsynchronousReliableWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous reliable messaging pattern."""
    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 inbound_queue_max_retries: int = None,
                 inbound_queue_retry_delay: int = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        super(AsynchronousReliableWorkflow, self).__init__(party_key, persistence_store, transmission,
                                                           queue_adaptor, inbound_queue_max_retries,
                                                           inbound_queue_retry_delay, persistence_store_max_retries,
                                                           routing)

        self.workflow_specific_interaction_details = dict(duplicate_elimination=True,
                                                          ack_requested=True,
                                                          ack_soap_actor="urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
                                                          sync_reply=True)

        self.soap_errors_to_retry = [SYSTEM_FAILURE_TO_PROCESS_MESSAGE_ERROR_CODE,
                                     ROUTING_DELIVERY_FAILURE_ERROR_CODE,
                                     FAILURE_STORING_VARIABLE_IN_MEMO]

    @timing.time_function
    async def handle_outbound_message(self, from_asid: Optional[str],
                                      message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      work_description_object: Optional[wd.WorkDescription]) \
            -> Tuple[int, str, Optional[wd.WorkDescription]]:

        logger.info('0001', 'Entered async reliable workflow to handle outbound message')
        if not work_description_object:
            wdo = wd.create_new_work_description(self.persistence_store,
                                                 message_id,
                                                 workflow.ASYNC_RELIABLE,
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

        # fetch the reliability details in case a retry is required
        reliability_details = await self._lookup_reliability_details(interaction_details)
        retry_interval = reliability_details[common_asynchronous.MHS_RETRY_INTERVAL][0]
        num_of_retries = reliability_details[common_asynchronous.MHS_RETRIES]

        retries_remaining = num_of_retries
        while True:
            try:
                response = await self.transmission.make_request(url, http_headers, message)
                end_time = timing.get_time()
            except httpclient.HTTPClientError as e:
                logger.warning('0005', 'Received HTTP errors from Spine. {HTTPStatus} {Exception}',
                               {'HTTPStatus': e.code, 'Exception': e})
                self._record_outbound_audit_log(workflow.ASYNC_RELIABLE,
                                                timing.get_time(),
                                                start_time,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)

                await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)

                if e.response:
                    # parse the SOAP error response
                    soap_fault_code, soap_body, soap_fault_codes = \
                        handle_soap_error(e.response.code, e.response.headers, e.response.body)

                    if not self._is_soap_fault_retriable(soap_fault_codes):
                        return soap_fault_code, soap_body

                    retries_remaining -= 1
                    logger.warning("0015",
                                   "A retriable error was encountered {exception} {retries_remaining} {max_retries}",
                                   {"exception": e,
                                    "retries_remaining": retries_remaining,
                                    "max_retries": num_of_retries
                                    })
                    if retries_remaining <= 0:
                        # exceeded the number of retries so return the SOAP error response
                        logger.error("0016",
                                     "A request has exceeded the maximum number of retries, {max_retries} retries",
                                     {"max_retries": num_of_retries})
                        raise MaxRetriesExceeded("The max number of retries to make the request has been exceeded") from e

                    logger.info("0016", "Waiting for {retry_interval} milliseconds before next request attempt.",
                                {"retry_interval": retry_interval})
                    await asyncio.sleep(retry_interval / 1000)
                    continue
                else:
                    return 500, f'Error(s) received from Spine: {e}'
            except Exception as e:
                logger.warning('0006', 'Error encountered whilst making outbound request. {Exception}', {'Exception': e})
                await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
                return 500, 'Error making outbound request'

            if response.code == 202:
                self._record_outbound_audit_log(workflow.ASYNC_RELIABLE,
                                                end_time,
                                                start_time,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
                await wd.update_status_with_retries(wdo, wdo.set_outbound_status, wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                                                    self.store_retries)
                return 202, ''
            else:
                logger.warning('0008', "Didn't get expected HTTP status 202 from Spine, got {HTTPStatus} instead",
                               {'HTTPStatus': response.code})
                self._record_outbound_audit_log(workflow.ASYNC_RELIABLE,
                                                end_time,
                                                start_time,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
                await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
                return 500, "Didn't get expected success response from Spine"

    @timing.time_function
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('0009', 'Entered async reliable workflow to handle inbound message')
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
                    logger.error("0012",
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

    def _is_soap_fault_retriable(self, soap_fault_codes):
        # return True only if ALL error codes are retriable
        for soap_fault_code in soap_fault_codes:
            if not soap_fault_code in self.soap_errors_to_retry:
                return False
        return True

    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        raise NotImplementedError()

    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        raise NotImplementedError()
