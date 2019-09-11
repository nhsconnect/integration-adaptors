"""This module defines the component used to orchestrate the retrieval and caching of routing and reliability
information for a remote MHS."""

from typing import Dict

from utilities import integration_adaptors_logger as log

import lookup.cache_adaptor as cache_adaptor
import lookup.sds_client as sds_client

logger = log.IntegrationAdaptorsLogger('SRL_ATTRIBUTE_LOOKUP')


class MHSAttributeLookup:
    """A tool that allows the routing and reliability information for a remote MHS to be retrieved."""

    def __init__(self, client: sds_client.SDSClient, cache: cache_adaptor.CacheAdaptor):
        """

        :param client The SDS client to use when retrieving remote MHS details.
        :param cache: The cache adaptor to use to cache remote MHS details.
        """
        if not client:
            raise ValueError('sds client required')
        if not cache:
            raise ValueError('No cache supplied')
        self.cache = cache
        self.sds_client = client

    async def retrieve_mhs_attributes(self, ods_code, interaction_id) -> Dict:
        """Obtains the attributes of the MHS registered for the given ODS code and interaction ID. These details will
        be obtained from the cache if available, and if not looked up using the SDS client and then cached for future
        calls.

        :param ods_code:
        :param interaction_id:
        :return:
        """
        cache_value = await self.cache.retrieve_mhs_attributes_value(ods_code, interaction_id)
        if cache_value:
            logger.info('0001', 'MHS details found in cache for {ods_code} & {interaction_id}',
                        {'ods_code': ods_code, 'interaction_id': interaction_id})
            return cache_value

        endpoint_details = await self.sds_client.get_mhs_details(ods_code, interaction_id)
        logger.info('0002', 'MHS details obtained from sds, adding to cache for {ods_code} & {interaction_id}',
                    {'ods_code': ods_code, 'interaction_id': interaction_id})
        await self.cache.add_cache_value(ods_code, interaction_id, endpoint_details)
        return endpoint_details
