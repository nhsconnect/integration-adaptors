"""This module defines the synchronous workflow."""
from typing import Tuple, Optional
import utilities.integration_adaptors_logger as log
from utilities import timing

from mhs_common import workflow
from mhs_common.errors.soap_handler import handle_soap_error
from tornado import httpclient

from mhs_common.state import persistence_adaptor as pa
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_synchronous

logger = log.IntegrationAdaptorsLogger('SYNC_WORKFLOW')


class SynchronousWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the synchronous messaging pattern."""

    def __init__(self,
                 party_key: str = None,
                 work_description_store: pa.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 persistence_store_max_retries: int = None):
        self.party_key = party_key
        self.wd_store = work_description_store
        self.transmission = transmission
        self.persistence_store_retries = persistence_store_max_retries

    async def handle_outbound_message(self,
                                      message_id: str,
                                      correlation_id: str,
                                      interaction_details: dict,
                                      payload: str,
                                      work_description_object: Optional[wd.WorkDescription]) -> Tuple[int, str]:
        logger.info('001', 'Entered sync workflow for outbound message')
        wdo = wd.create_new_work_description(self.wd_store,
                                             message_id,
                                             workflow.SYNC,
                                             wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED
                                             )
        await wdo.publish()

        try:
            headers, message = await self._prepare_outbound_message()
        except Exception as e:
            # Failed to prepare message
            logger.warning('002', 'Failed to prepare outbound message')
            return 500, 'Failed message preparation'

        logger.info('003', 'About to make outbound request')
        start_time = timing.get_time()
        try:
            url = interaction_details['url']
            response = await self.transmission.make_request(url, headers, message)
            end_time = timing.get_time()
        except httpclient.HTTPClientError as e:
            logger.warning('0005', 'Received HTTP errors from Spine. {HTTPStatus} {Exception}',
                           {'HTTPStatus': e.code, 'Exception': e})
            self._record_outbound_audit_log(timing.get_time(), start_time,
                                            wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)

            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)

            if e.response:
                return handle_soap_error(e.response.code, e.response.headers, e.response.body)

            return 500, f'Error(s) received from Spine: {e}'
        except Exception as e:
            logger.warning('0006', 'Error encountered whilst making outbound request. {Exception}', {'Exception': e})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error making outbound request'

        if response.code == 200:
            self._record_outbound_audit_log(end_time, start_time, wd.MessageStatus.OUTBOUND_MESSAGE_RES)
            await wd.update_status_with_retries(wdo,
                                                wdo.set_outbound_status,
                                                wd.MessageStatus.OUTBOUND_MESSAGE_RESPONSE_RECEIVED,
                                                self.persistence_store_retries)
            return 202, ''
        else:
            logger.warning('0008', "Didn't get expected HTTP status 202 from Spine, got {HTTPStatus} instead",
                           {'HTTPStatus': response.code})
            self._record_outbound_audit_log(end_time, start_time, wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            return 500, "Didn't get expected success response from Spine"

        return (200, "qwe")

    async def _prepare_outbound_message(self):
        return {}, "empty"

    def _record_outbound_audit_log(self, end_time, start_time, acknowledgment):
        logger.audit('0007', 'Synchronous workflow invoked. Message sent to Spine and {Acknowledgment} received. '
                             '{RequestSentTime} {AcknowledgmentReceivedTime}',
                     {'RequestSentTime': start_time, 'AcknowledgmentReceivedTime': end_time,
                      'Acknowledgment': acknowledgment})

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        raise NotImplementedError('This method is not supported for the synchronous message workflow as there is no '
                                  'inbound message')
