from mhs.routing import sds_handler

RELIABILITY_KEYS = [
    'nhsMHSSyncReplyMode',
    'nhsMHSRetryInterval',
    'nhsMHSRetries',
    'nhsMHSPersistDuration',
    'nhsMHSDuplicateElimination',
    'nhsMHSAckRequested'
]

ROUTING_KEYS = ['nhsMhsFQDN', 'nhsMHSEndPoint']


class RoutingAndReliability:

    def __init__(self, lookup_handler: sds_handler.MHSAttributeLookupHandler):
        if not lookup_handler:
            raise ValueError("MHS Attribute Lookup not found")
        self.lookup = lookup_handler

    async def get_end_point(self, org_code, service_id):
        endpoint_details = await self.lookup.retrieve_mhs_attributes(org_code, service_id)
        routing = {item: endpoint_details[item] for item in ROUTING_KEYS}

        return routing

    async def get_reliability(self, org_code, service_id):
        endpoint_details = await self.lookup.retrieve_mhs_attributes(org_code, service_id)

        reliability = {item: endpoint_details[item] for item in RELIABILITY_KEYS}
        return reliability
