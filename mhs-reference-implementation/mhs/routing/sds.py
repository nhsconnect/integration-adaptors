import asyncio
import logging
import ldap3
from mhs.routing import routing_exception
import ldap3.core.exceptions as ldap_exceptions
from typing import Dict, List

logger = logging.getLogger(__name__)

NHS_SERVICES_BASE = "ou=services, o=nhs"

MHS_OBJECT_CLASS = "nhsMhs"
AS_OBJECT_CLASS = "nhsAs"
MHS_PARTY_KEY = 'nhsMHSPartyKey'

mhs_attributes = [
    'nhsEPInteractionType', 'nhsIDCode', 'nhsMhsCPAId', 'nhsMHSEndPoint', 'nhsMhsFQDN',
    'nhsMHsIN', 'nhsMHSIsAuthenticated', 'nhsMHSPartyKey', 'nhsMHsSN', 'nhsMhsSvcIA', 'nhsProductKey',
    'uniqueIdentifier', 'nhsMHSAckRequested', 'nhsMHSActor', 'nhsMHSDuplicateElimination',
    'nhsMHSPersistDuration', 'nhsMHSRetries', 'nhsMHSRetryInterval', 'nhsMHSSyncReplyMode'
]


class SDSClient:

    def __init__(self, sds_connection: ldap3.Connection, timeout: int = 3):
        """
        :param sds_connection: takes an ldap connection to the sds server
        """
        if not sds_connection:
            raise ValueError('sds_connection must not be null')

        self.connection = sds_connection
        self.timeout = timeout

    async def get_mhs_details(self, ods_code: str, interaction_id: str) -> Dict:
        """
        Returns the mhs details for the given org code and interaction id
        :param ods_code:
        :param interaction_id:
        :return:
        """

        accredited_system_lookup = await self._accredited_system_lookup(ods_code, interaction_id)

        if not accredited_system_lookup:
            raise routing_exception.RoutingException('No response from accredited system lookup')

        if len(accredited_system_lookup) > 1:
            logger.warning(f"More than one accredited system details returned on inputs: "
                           f"ods: {ods_code} - interaction: {interaction_id}")

        # As per the spec exactly one result should be returned
        response = accredited_system_lookup[0]
        party_key = response['attributes'][MHS_PARTY_KEY]

        details = await self._mhs_details_lookup(party_key, interaction_id)

        if len(details) > 1:
            logger.warning(f"More than one mhs details returned on inputs: "
                           f"ods: {ods_code} - interaction: {interaction_id}")
        return details[0]['attributes']

    async def _accredited_system_lookup(self, ods_code: str, interaction_id: str) -> List:
        """
        Used to find an accredited system, the result contains the nhsMhsPartyKey.
        This can then be used to find an MHS endpoint
        :return: endpoint details - filtered to only contain nhsMHSPartyKey
        """

        search_filter = f"(&(nhsIDCode={ods_code}) (objectClass={AS_OBJECT_CLASS}) (nhsAsSvcIA={interaction_id}))"

        message_id = self.connection.search(search_base=NHS_SERVICES_BASE,
                                            search_filter=search_filter,
                                            attributes=MHS_PARTY_KEY)
        logger.info(f'Message id - {message_id} - for query: ods code - {ods_code} '
                    f': interaction id - {interaction_id}')

        query_task = self._get_query_result(message_id)
        response = await query_task
        return response

    async def _mhs_details_lookup(self, party_key: str, interaction_id: str) -> List:
        """
        Given a party key and a service, this will return an object containing the attributes of that party key,
        including the endpoint address
        :param party_key:
        :param interaction_id:
        :return: all the endpoint details
        """
        search_filter = f"(&(objectClass={MHS_OBJECT_CLASS})" \
            f" ({MHS_PARTY_KEY}={party_key})" \
            f" (nhsMhsSvcIA={interaction_id}))"
        message_id = self.connection.search(search_base=NHS_SERVICES_BASE,
                                            search_filter=search_filter,
                                            attributes=mhs_attributes)

        logger.info(f'Message id - {message_id} - for query: party key - {party_key} '
                    f': interaction id - {interaction_id}')

        query_task = self._get_query_result(message_id)
        response = await query_task
        return response

    async def _get_query_result(self, message_id: int) -> List:
        loop = asyncio.get_event_loop()
        try:
            response, result = await loop.run_in_executor(None, self.connection.get_response, message_id, self.timeout)
        except ldap_exceptions.LDAPResponseTimeoutError:
            logger.error(f'LDAP query timed out for message id: {message_id}')
            return []

        return response
