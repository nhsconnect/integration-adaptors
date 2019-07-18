"""This module defines the component used to look up routing and reliability information for a remote MHS."""

import mhs.message_configuration.lookup.mhs_attribute_lookup as mhs_attribute_lookup


class RoutingAndReliability:
    """A tool that allows the routing and reliability information for a remote MHS to be retrieved."""

    def __init__(self, lookup_handler: mhs_attribute_lookup.MHSAttributeLookup):
        pass

    async def get_end_point(self, org_code, service_id):
        """Get the endpoint of the MHS registered for the specified org code and service ID.

        :param org_code:
        :param service_id:
        :return:
        """
        pass

    async def get_reliability(self, org_code, service_id):
        """Get the reliability information for the MHS registered for the specified org code and service ID.

        :param org_code:
        :param service_id:
        :return:
        """
        pass
