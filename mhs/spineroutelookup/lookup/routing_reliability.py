"""This module defines the component used to look up routing and reliability information for a remote MHS."""

import lookup.mhs_attribute_lookup as mhs_attribute_lookup

RELIABILITY_KEYS = [
    'nhsMHSSyncReplyMode',
    'nhsMHSRetryInterval',
    'nhsMHSRetries',
    'nhsMHSPersistDuration',
    'nhsMHSDuplicateElimination',
    'nhsMHSAckRequested'
]

ROUTING_KEYS = ['nhsMhsFQDN', 'nhsMHSEndPoint', 'nhsMHSPartyKey', 'nhsMhsCPAId', 'uniqueIdentifier']


class RoutingAndReliability(object):
    """A tool that allows the routing and reliability information for a remote MHS to be retrieved."""

    def __init__(self, lookup_handler: mhs_attribute_lookup.MHSAttributeLookup):
        if not lookup_handler:
            raise ValueError("MHS Attribute Lookup Handler not found")
        self.lookup = lookup_handler

    async def get_end_point(self, org_code, service_id):
        """Get the endpoint of the MHS registered for the specified org code and service ID.

        :param org_code:
        :param service_id:
        :return:
        """
        endpoint_details = await self.lookup.retrieve_mhs_attributes(org_code, service_id)
        routing = {item: endpoint_details[item] for item in ROUTING_KEYS}
        return routing

    async def get_reliability(self, org_code, service_id):
        """Get the reliability information for the MHS registered for the specified org code and service ID.

        :param org_code:
        :param service_id:
        :return:
        """
        endpoint_details = await self.lookup.retrieve_mhs_attributes(org_code, service_id)

        reliability = {item: endpoint_details[item] for item in RELIABILITY_KEYS}
        return reliability
