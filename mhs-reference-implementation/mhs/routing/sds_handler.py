import mhs.routing.sds as sds
from mhs.routing import abstract_cache_adapter


class MHSAttributeLookupHandler:

    def __init__(self, client: sds.SDSClient, cache: abstract_cache_adapter.AbstractMHSCacheAdaptor):
        if not client:
            raise ValueError('sds client required')
        if not cache:
            raise ValueError('No cache supplied')
        self.cache = cache
        self.sds_client = client

    async def retrieve_mhs_attributes(self, ods_code, interaction_id):
        cache_value = await self.cache.retrieve_mhs_attributes_value(ods_code, interaction_id)
        if cache_value:
            return cache_value

        endpoint_details = await self.sds_client.get_mhs_details(ods_code, interaction_id)

        await self.cache.add_cache_value(ods_code, interaction_id, endpoint_details)
        return endpoint_details
