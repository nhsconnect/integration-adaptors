"""This module defines the asynchronous forward reliable workflow."""
from typing import Tuple, Optional

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from exceptions import MaxRetriesExceeded
from isodate import isoerror
from retry import retriable_action
from mhs_common.workflow.common import MessageData
from utilities import timing, config
from utilities.date_utilities import DateUtilities

from mhs_common import workflow
from mhs_common.routing import routing_reliability
from persistence import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_asynchronous, asynchronous_reliable

logger = log.IntegrationAdaptorsLogger(__name__)


class AsynchronousForwardReliableWorkflow(asynchronous_reliable.AsynchronousReliableWorkflow):
    """Handles the workflow for the asynchronous forward reliable messaging pattern."""

    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 max_request_size: int = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        super().__init__(party_key, persistence_store, transmission,
                         queue_adaptor, max_request_size, persistence_store_max_retries,
                         routing)

        self.workflow_specific_interaction_details = dict(
            ack_soap_actor="urn:oasis:names:tc:ebxml-msg:actor:nextMSH",
            duplicate_elimination=True,
            ack_requested=True,
            sync_reply=False)

        self.workflow_name = workflow.FORWARD_RELIABLE

    @timing.time_function
    async def handle_outbound_message(self, from_asid: Optional[str],
                                      message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      wdo: Optional[wd.WorkDescription]) \
            -> Tuple[int, str, Optional[wd.WorkDescription]]:

        logger.info('Entered async forward reliable workflow to handle outbound message')
        logger.audit('Outbound {WorkflowName} workflow invoked.', fparams={'WorkflowName': self.workflow_name})
        wdo = await self._create_new_work_description_if_required(message_id, wdo, self.workflow_name)

        try:
            details = await self._lookup_endpoint_details(interaction_details)
            url = config.get_config("FORWARD_RELIABLE_ENDPOINT_URL")
            to_party_key = details[self.ENDPOINT_PARTY_KEY]
            cpa_id = details[self.ENDPOINT_CPA_ID]
        except Exception:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
            return 500, 'Error obtaining outbound URL', None

        reliability_details = await self._lookup_reliability_details(interaction_details,
                                                                     interaction_details.get('ods-code'))
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

    @timing.time_function
    async def handle_unsolicited_inbound_message(self, message_id: str, correlation_id: str, message_data: MessageData):
        logger.info('Entered async forward reliable workflow to handle unsolicited inbound message')
        logger.audit('Unsolicited inbound {WorkflowName} workflow invoked.',
                     fparams={'WorkflowName': self.workflow_name})
        work_description = wd.create_new_work_description(self.persistence_store, message_id, self.workflow_name,
                                                          wd.MessageStatus.UNSOLICITED_INBOUND_RESPONSE_RECEIVED)
        await work_description.publish()

        try:
            await self._put_message_onto_queue_with(message_id, correlation_id, message_data)
        except Exception as e:
            await work_description.set_inbound_status(wd.MessageStatus.UNSOLICITED_INBOUND_RESPONSE_FAILED)
            raise e

        logger.audit('{WorkflowName} workflow invoked for inbound unsolicited request. '
                     'Attempted to place message onto inbound queue with {Acknowledgement}.',
                     fparams={
                        'Acknowledgement': wd.MessageStatus.UNSOLICITED_INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED,
                        'WorkflowName': self.workflow_name
                     })
        await work_description.set_inbound_status(wd.MessageStatus.UNSOLICITED_INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)
