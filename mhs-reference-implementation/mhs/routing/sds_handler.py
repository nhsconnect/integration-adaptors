import logging
import mhs.routing.sds as sds
from mhs.routing import abstract_cache_adapter as aca
from typing import Dict

logger = logging.getLogger(__name__)


class MHSAttributeLookupHandler:

    def __init__(self, client: sds.SDSClient, cache: aca.AbstractMHSCacheAdaptor):
        if not client:
            raise ValueError('sds client required')
        if not cache:
            raise ValueError('No cache supplied')
        self.cache = cache
        self.sds_client = client

    async def retrieve_mhs_attributes(self, ods_code, interaction_id) -> Dict:
        cache_value = await self.cache.retrieve_mhs_attributes_value(ods_code, interaction_id)
        if cache_value:
            logger.info(f'MHS details found in cache for ods code: {ods_code} & interaction id: {interaction_id}')
            return cache_value

        endpoint_details = await self.sds_client.get_mhs_details(ods_code, interaction_id)
        logger.info(f'MHS details obtained from sds, adding to cache for ods code: {ods_code} '
                    f'interaction id: {interaction_id}')
        await self.cache.add_cache_value(ods_code, interaction_id, endpoint_details)
        return endpoint_details
