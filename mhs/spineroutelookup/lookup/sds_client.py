"""This module contains the client used to make requests to SDS."""

import asyncio
from typing import Dict, List

import ldap3
import ldap3.core.exceptions as ldap_exceptions

from lookup import sds_connection_factory
from utilities import integration_adaptors_logger as log

import lookup.sds_exception as sds_exception

logger = log.IntegrationAdaptorsLogger(__name__)

MHS_OBJECT_CLASS = "nhsMhs"
AS_OBJECT_CLASS = "nhsAs"
MHS_PARTY_KEY = 'nhsMHSPartyKey'
MHS_ASID = 'uniqueIdentifier'

mhs_attributes = [
    'nhsEPInteractionType', 'nhsIDCode', 'nhsMhsCPAId', 'nhsMHSEndPoint', 'nhsMhsFQDN',
    'nhsMHsIN', 'nhsMHSIsAuthenticated', 'nhsMHSPartyKey', 'nhsMHsSN', 'nhsMhsSvcIA', 'nhsProductKey',
    'uniqueIdentifier', 'nhsMHSAckRequested', 'nhsMHSActor', 'nhsMHSDuplicateElimination',
    'nhsMHSPersistDuration', 'nhsMHSRetries', 'nhsMHSRetryInterval', 'nhsMHSSyncReplyMode'
]


class SDSClient(object):
    """A client that can be used to query SDS."""

    def __init__(self, sds_connection: ldap3.Connection, search_base: str, timeout: int = 3):
        """
        :param sds_connection: takes an ldap connection to the sds server
        :param search_base: The LDAP location to use as the base of SDS searches. e.g. ou=services,o=nhs.
        :param timeout The amount of time to wait for an LDAP query to complete.
        """
        if not sds_connection:
            raise ValueError('sds_connection must not be null')

        if not search_base:
            raise ValueError('search_base must be specified')

        self.connection = sds_connection
        self.timeout = timeout
        self.search_base = search_base

    async def get_mhs_details(self, ods_code: str, interaction_id: str) -> Dict:
        """
        Returns the mhs details for the given org code and interaction ID.

        :return: Dictionary of the attributes of the mhs associated with the given parameters
        """

        accredited_system_lookup = await self._accredited_system_lookup(ods_code, interaction_id)

        if not accredited_system_lookup:
            logger.error("Failed to find accredited system details for {ods_code} & {interaction_id}",
                         fparams={"ods_code": ods_code, "interaction_id": interaction_id})
            raise sds_exception.SDSException('No response from accredited system lookup')

        if len(accredited_system_lookup) > 1:
            logger.warning("More than one accredited system details returned on inputs: {ods_code} & "
                           "{interaction_id}", fparams={"ods_code": ods_code, "interaction_id": interaction_id})

        # As per the spec exactly one result should be returned
        response = accredited_system_lookup[0]
        party_key = response['attributes'][MHS_PARTY_KEY]

        asid = response['attributes'].get(MHS_ASID)

        details = await self._mhs_details_lookup(party_key, interaction_id)

        if not details:
            logger.error("No mhs details returned for {party_key} & {interaction_id}",
                         fparams={"party_key": party_key, "interaction_id": interaction_id})
            raise sds_exception.SDSException(f'No mhs details returned for party key: '
                                             f'{party_key} and interaction id : {interaction_id}')
        if len(details) > 1:
            logger.warning("More than one mhs details returned on inputs: {ods_code} & {interaction_id}",
                           fparams={"ods_code": ods_code, "interaction_id": interaction_id})

        details[0]['attributes'][MHS_ASID] = asid
        return dict(details[0]['attributes'])

    async def _accredited_system_lookup(self, ods_code: str, interaction_id: str) -> List:
        """
        Used to find an accredited system, the result contains the nhsMhsPartyKey.
        This can then be used to find an MHS endpoint
        :return: endpoint details - filtered to only contain nhsMHSPartyKey
        """

        search_filter = f"(&(nhsIDCode={ods_code}) (objectClass={AS_OBJECT_CLASS}) (nhsAsSvcIA={interaction_id}))"
        self.connection.bind()
        try:
            message_id = self.connection.search(search_base=self.search_base,
                                            search_filter=search_filter,
                                            attributes=[MHS_PARTY_KEY, MHS_ASID])
            logger.info("{message_id} - for query: {ods_code} {interaction_id}",
                    fparams={"message_id": message_id, "ods_code": ods_code, "interaction_id": interaction_id})
        except ldap_exceptions.LDAPExceptionError as e:
            logger.exception(e)
            logger.info("LDAP error occurred trying to reconnect")
            self.connection = sds_connection_factory.create_connection()
            self.connection.bind()
            message_id = self.connection.search(search_base=self.search_base,
                                                search_filter=search_filter,
                                                attributes=[MHS_PARTY_KEY, MHS_ASID])
            logger.info("{message_id} - for query: {ods_code} {interaction_id}",
                        fparams={"message_id": message_id, "ods_code": ods_code, "interaction_id": interaction_id})

        response = await self._get_query_result(message_id)
        logger.info("Found accredited supplier details for {message_id}", fparams={"message_id": message_id})

        return response

    async def _mhs_details_lookup(self, party_key: str, interaction_id: str) -> List:
        """
        Given a party key and an interaction id, this will return an object containing the attributes of that party key,
        including the endpoint address
        :return: all the endpoint details
        """
        search_filter = f"(&(objectClass={MHS_OBJECT_CLASS})" \
            f" ({MHS_PARTY_KEY}={party_key})" \
            f" (nhsMhsSvcIA={interaction_id}))"
        message_id = self.connection.search(search_base=self.search_base,
                                            search_filter=search_filter,
                                            attributes=mhs_attributes)

        logger.info("{message_id} - for query: {party_key} {interaction_id}",
                    fparams={"message_id": message_id, "party_key": party_key, "interaction_id": interaction_id})

        response = await self._get_query_result(message_id)
        logger.info("Found mhs details for {message_id}", fparams={"message_id": message_id})

        return response

    async def _get_query_result(self, message_id: int) -> List:
        loop = asyncio.get_event_loop()
        response = []
        try:
            response, result = await loop.run_in_executor(None, self.connection.get_response, message_id, self.timeout)
        except ldap_exceptions.LDAPResponseTimeoutError:
            logger.error("LDAP query timed out for {message_id}", fparams={"message_id": message_id})

        return response
