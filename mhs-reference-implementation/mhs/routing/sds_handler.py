
import mhs.routing.sds as sds


class MHSAttributeLookupHandler:

    def __init__(self, sds_lookup_address: str = None):
        self.cache = {}
        self.sds_client = sds.SDSClient(sds_lookup_address)

    async def retrieve_mhs_attributes(self, org_code, service_id):
        # Check cache for hits, if no hit retrieve via sds client
        endpoint_details = await self.sds_client.get_mhs_details(org_code, service_id)

        # cache.add(endpoint_details)
        return endpoint_details
