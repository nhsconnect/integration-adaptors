"""This module defines the component used to orchestrate the retrieval and caching of routing and reliability
information for a remote MHS."""

import mhs.message_configuration.lookup.sds_client as sds_client
import mhs.message_configuration.lookup.cache_adapter as cache_adapter


class MHSAttributeLookup:
    """A tool that allows the routing and reliability information for a remote MHS to be retrieved."""

    def __init__(self, client: sds_client.SDSClient, cache: cache_adapter.CacheAdapter):
        """

        :param client The SDS client to use when retrieving remote MHS details.
        :param cache: The cache adapter to use to cache remote MHS details.
        """
        pass

    async def retrieve_mhs_attributes(self, ods_code, interaction_id) -> Dict:
        """Obtains the attributes of the MHS registered for the given ODS code and interaction ID. These details will
        be obtained from the cache if available, and if not looked up using the SDS client and then cached for future
        calls.

        :param ods_code:
        :param interaction_id:
        :return:
        """
        pass
