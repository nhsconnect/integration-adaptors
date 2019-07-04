from mhs.routing import sds_handler


class RoutingAndReliability:

    def __init__(self, sds: sds_handler.MHSAttributeLookupHandler, cache):
        self.lookup = sds_handler.MHSAttributeLookupHandler(sds, cache)

    async def get_end_point(self, org_code, service_id):
        endpoint_details = await self.lookup.retrieve_mhs_attributes(org_code, service_id)

        first_endpoint = endpoint_details[0]['attributes']['nhsMHSEndPoint']

        return first_endpoint[0]

    async def get_reliability(self, org_code, service_id):
        endpoint_details = await self.lookup.retrieve_mhs_attributes(org_code, service_id)
        first_endpoint = endpoint_details[0]['attributes']

        reliability_strings = ['nhsMHSAckRequested', 'nhsMHSDuplicateElimination', 'nhsMHSPersistDuration',
                               'nhsMHSRetries', 'nhsMHSRetryInterval']
        reliability = {item: first_endpoint[item] for item in reliability_strings}
        return reliability
