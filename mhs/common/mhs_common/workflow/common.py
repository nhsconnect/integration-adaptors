"""This module defines the common base of all workflows."""
import abc
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, List

import utilities.integration_adaptors_logger as log

import mhs_common.state.work_description as wd
from mhs_common.messages import ebxml_envelope
from mhs_common.routing import routing_reliability

MHS_END_POINT_KEY = 'nhsMHSEndPoint'
MHS_TO_PARTY_KEY_KEY = 'nhsMHSPartyKey'
MHS_CPA_ID_KEY = 'nhsMhsCPAId'
MHS_TO_ASID_KEY = 'uniqueIdentifier'

logger = log.IntegrationAdaptorsLogger(__name__)


@dataclass
class MessageData:
    ebxml: str
    payload: str
    attachments: List


class CommonWorkflow(abc.ABC):
    """Common functionality across all workflows."""

    ENDPOINT_URL = 'url'
    ENDPOINT_PARTY_KEY = 'party_key'
    ENDPOINT_TO_ASID = 'to_asid'
    ENDPOINT_SERVICE_ID = 'service_id'
    ENDPOINT_CPA_ID = 'cpa_id'

    workflow_name: str

    def __init__(self, routing: routing_reliability.RoutingAndReliability = None):
        self.routing_reliability = routing
        self.workflow_specific_interaction_details = dict()

    @abc.abstractmethod
    async def handle_outbound_message(self, from_asid: Optional[str],
                                      message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str,
                                      work_description_object: Optional[wd.WorkDescription]
                                      ) -> Tuple[int, str, Optional[wd.WorkDescription]]:
        """
        Handle a message from the supplier system (or a message from an adaptor that the supplier system speaks to)
        that is to be sent outbound.

        :param from_asid: Optional asid of the supplier system
        :param work_description_object: A potentially null value for the work description object for this message, if
                not present the child implementation is expected to generate this work description instance
        :param message_id: ID of the message to send
        :param correlation_id: correlation ID of the request
        :param interaction_details: interaction details used to construct the message to send outbound
        :param payload: payload to send outbound
        :return: the HTTP status, body to return as a response, and optionally the work description.
        The work description only needs to be returned if set_successful_message_response and/or
        set_failure_message_response are implemented for the workflow.
        """
        pass

    @abc.abstractmethod
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     message_data: MessageData):
        """
        Handles an inbound message from an external system (typically from spine)

        :param message_id: ID of the message the original request to Spine was made with
        :param correlation_id: correlation ID of the request
        :param work_description: work description object for the payload
        :param message_data: object consolidating the ebXML, payload and attachments
        """
        pass

    @abc.abstractmethod
    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        """
        Sets the work description status value to be a value that indicates the final message to the supplier was
        sent successfully
        :param wdo: The work description object
        """
        pass

    @abc.abstractmethod
    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        """
        Sets the work description status value to be a value that indicates the final message to the supplier was
        sent successfully
        :param wdo: The work description object
        """
        pass

    async def _lookup_endpoint_details(self, interaction_details: Dict) -> Dict:
        try:
            service_id = await self._build_service_id(interaction_details)

            ods_code = interaction_details.get('ods-code')
            if ods_code:
                logger.info('Looking up endpoint details for ods code: {ods_code}.', fparams={'ods_code': ods_code})

            logger.info('Looking up endpoint details for {service_id}.', fparams={'service_id': service_id})
            endpoint_details = await self.routing_reliability.get_end_point(service_id, ods_code)

            url = CommonWorkflow._extract_endpoint_url(endpoint_details)
            to_party_key = endpoint_details[MHS_TO_PARTY_KEY_KEY]
            cpa_id = endpoint_details[MHS_CPA_ID_KEY]
            to_asid = self._extract_asid(endpoint_details)
            details = {self.ENDPOINT_SERVICE_ID: service_id,
                       self.ENDPOINT_URL: url,
                       self.ENDPOINT_PARTY_KEY: to_party_key,
                       self.ENDPOINT_CPA_ID: cpa_id,
                       self.ENDPOINT_TO_ASID: to_asid
                       }
            logger.info('Retrieved endpoint details for {details}', fparams={'details': details})
            return details
        except Exception:
            logger.exception('Error encountered whilst retrieving endpoint details.')
            raise

    @staticmethod
    def _extract_endpoint_url(endpoint_details: Dict[str, List[str]]) -> str:
        endpoint_urls = endpoint_details[MHS_END_POINT_KEY]

        if len(endpoint_urls) == 0:
            logger.error('Did not receive any endpoint URLs when looking up endpoint details.')
            raise IndexError("Did not receive any endpoint URLs when looking up endpoint details.")

        url = endpoint_urls[0]

        if len(endpoint_urls) > 1:
            logger.warning('Received more than one URL when looking up endpoint details. Using {url}. {urls_received}',
                           fparams={'url': url, 'urls_received': endpoint_urls})

        return url

    @staticmethod
    def _extract_asid(endpoint_details: Dict[str, List[str]]) -> str:
        unique_identifiers = endpoint_details.get(MHS_TO_ASID_KEY)

        if not unique_identifiers:
            logger.error('Did not retrieve any unique identifiers from endpoint details')
            raise IndexError()

        asid = unique_identifiers[0]

        if len(unique_identifiers) > 1:
            logger.warning('Received more than one ASID during endpoint lookup')

        return asid

    @staticmethod
    async def _build_service_id(interaction_details):
        service = interaction_details[ebxml_envelope.SERVICE]
        action = interaction_details[ebxml_envelope.ACTION]

        service_id = service + ":" + action

        return service_id
