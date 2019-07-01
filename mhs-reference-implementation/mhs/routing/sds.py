import asyncio
import logging
import ssl
import pathlib
from definitions import ROOT_DIR
import ldap3
import mhs.routing.routing_exception as re

NHS_SERVICES_BASE = "ou=services, o=nhs"

MHS_OBJECT_CLASS = "nhsMhs"
AS_OBJECT_CLASS = "nhsAs"
MHS_PARTY_KEY = 'nhsMHSPartyKey'

# These need replacing as the appropriate TLS certs are received for PTL
PRIVATE_KEY = pathlib.Path(ROOT_DIR) / 'data' / 'certs' / 'client.key'
LOCAL_CERT_FILE = pathlib.Path(ROOT_DIR) / 'data' / 'certs' / 'client.cert'
CA_CERTS_FILE = pathlib.Path(ROOT_DIR) / 'data' / 'certs' / 'client.cert'

mhs_attributes = [
    'nhsEPInteractionType', 'nhsIDCode', 'nhsMhsCPAId', 'nhsMHSEndPoint', 'nhsMhsFQDN',
    'nhsMHsIN', 'nhsMHSIsAuthenticated', 'nhsMHSPartyKey', 'nhsMHsSN', 'nhsMhsSvcIA', 'nhsProductKey',
    'uniqueIdentifier', 'nhsMHSAckRequested', 'nhsMHSActor', 'nhsMHSDuplicateElimination',
    'nhsMHSPersistDuration', 'nhsMHSRetries', 'nhsMHSRetryInterval', 'nhsMHSSyncReplyMode'
]


class SDSClient:

    def __init__(self, ldap_address: str = None, tls: bool = False):
        """
        :param ldap_address: The IP address of the directory containing data of the the MHSs
        :param tls: Boolean defining whether or not to use TLS, this will require SSL certs to the LDAP server
        """
        load_tls = None
        if ldap_address:
            if tls:
                load_tls = ldap3.Tls(local_private_key_file=PRIVATE_KEY,
                                     local_certificate_file=LOCAL_CERT_FILE,
                                     validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1,
                                     ca_certs_file=CA_CERTS_FILE)

            server = ldap3.Server(ldap_address, use_ssl=tls, tls=load_tls)
            self.connection = ldap3.Connection(server, auto_bind=True, client_strategy=ldap3.REUSABLE)
        else:
            self.connection = None

    async def get_mhs_details(self, ods_code: str, interaction_id: str):
        """
        Returns the mhs details for the given org code and interaction id
        :param ods_code:
        :param interaction_id:
        :return:
        """

        accredited_system_lookup = await self._accredited_system_lookup(ods_code, interaction_id)

        if not accredited_system_lookup:
            raise re.RoutingException('No response from accredited system lookup')

        if len(accredited_system_lookup) > 1:
            logging.warning(f"More than one accredited system details returned on inputs: "
                            f"ods: {ods_code} - interaction: {interaction_id}")
        # As per the spec exactly one result should be returned

        response = accredited_system_lookup[0]
        party_key = response['attributes'][MHS_PARTY_KEY]

        details = await self._mhs_details_lookup(party_key, interaction_id)

        if len(details) > 1:
            logging.warning(f"More than one mhs details  returned on inputs: "
                            f"ods: {ods_code} - interaction: {interaction_id}")
        return details[0]['attributes']

    async def _accredited_system_lookup(self, ods_code: str, interaction_id: str):
        """
        Used to find an accredited system, the result contains the nhsMhsPartyKey.
        This can then be used to find an MHS endpoint
        :return: endpoint details - filtered to only contain nhsMHSPartyKey
        """
        if not self.connection:
            raise IOError('No connection established')

        search_filter = f"(&(nhsIDCode={ods_code}) (objectClass={AS_OBJECT_CLASS}) (nhsAsSvcIA={interaction_id}))"

        message_id = self.connection.search(search_base=NHS_SERVICES_BASE,
                                            search_filter=search_filter,
                                            attributes="nhsMHSPartyKey")

        query_task = self._get_query_result(message_id)
        response = await query_task
        return response

    async def _mhs_details_lookup(self, party_key: str, interaction_id: str):
        """
        Given a party key and a service, this will return an object containing the attributes of that party key,
        including the endpoint address
        :param party_key:
        :param interaction_id:
        :return: all the endpoint details
        """
        if not self.connection:
            raise IOError('No connection established')

        search_filter = f"(&(objectClass={MHS_OBJECT_CLASS}) (nhsMhsPartyKey={party_key}) (nhsMhsSvcIA={interaction_id}))"
        message_id = self.connection.search(search_base=NHS_SERVICES_BASE,
                                            search_filter=search_filter,
                                            attributes=mhs_attributes)

        query_task = self._get_query_result(message_id)
        response = await query_task
        return response

    async def _get_query_result(self, message_id):
        response, result = self.connection.get_response(message_id)
        return response
