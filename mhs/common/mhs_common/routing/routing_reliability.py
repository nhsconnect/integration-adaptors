import json
from typing import Dict

from comms import common_https
from utilities import integration_adaptors_logger as log, timing

ROUTING_PATH = "routing"
RELIABILITY_PATH = "reliability"

logger = log.IntegrationAdaptorsLogger("MHS_ROUTING_RELIABILITY")


class RoutingAndReliability:
    """A tool that allows the routing and reliability information for a remote MHS to be retrieved."""

    def __init__(self, spine_route_lookup_url: str, spine_org_code: str):
        """Initialise a new RoutingAndReliability instance.

        :param spine_route_lookup_url: The URL to make requests to the Spine Route Lookup service on. e.g.
        http://example.com. This URL should not contain path or query parameter parts.
        :param spine_org_code The organisation code of the Spine instance this MHS is communicating with.
        """
        self.url = spine_route_lookup_url
        self.spine_org_code = spine_org_code

    @timing.time_function
    async def get_end_point(self, service_id: str, org_code: str = None) -> Dict:
        """Get the endpoint of the MHS registered for the specified org code and service ID.

        :param service_id: The ID of the service to get MHS details for.
        :param org_code: The org code of the MHS to get details for. If not provided, the org code configured for Spine
        is used.
        :return: A dictionary containing the end point information.
        """
        if org_code is None:
            org_code = self.spine_org_code
            logger.info("0007", "No org code provided when obtaining endpoint details. Using {spine_org_code}",
                        {"spine_org_code": org_code})

        url = self._build_request_url(ROUTING_PATH, org_code, service_id)

        try:

            logger.info("0001", "Requesting endpoint details from Spine route lookup service for {org_code} & "
                                "{service_id}.", {"org_code": org_code, "service_id": service_id})
            http_response = await common_https.CommonHttps.make_request(url=url, method="GET", headers=None, body=None)
            endpoint_details = json.loads(http_response.body)

            logger.info("0002", "Received endpoint details from Spine route lookup service for {org_code} & "
                                "{service_id}. {endpoint_details}",
                        {"org_code": org_code, "service_id": service_id, "endpoint_details": endpoint_details})
            return endpoint_details
        except Exception as e:
            logger.error("0003",
                         "Couldn't obtain endpoint details from Spine route lookup service for {org_code} & "
                         "{service_id}. {exception}", {"org_code": org_code, "service_id": service_id, "exception": e})
            raise e

    @timing.time_function
    async def get_reliability(self, service_id: str, org_code: str = None) -> Dict:
        """Get the reliability information for the MHS registered for the specified org code and service ID.

        :param org_code: The org code of the MHS to get details for. If not provided, the org code configured for Spine
        is used.
        :param service_id: The ID of the service to get MHS details for.
        :return: A dictionary containing the reliability information.
        """
        if org_code is None:
            org_code = self.spine_org_code
            logger.info("0008", "No org code provided when obtaining reliability details. Using {spine_org_code}",
                        {"spine_org_code": org_code})

        url = self._build_request_url(RELIABILITY_PATH, org_code, service_id)

        try:
            logger.info("0004", "Requesting reliability details from Spine route lookup service for {org_code} & "
                                "{service_id}.", {"org_code": org_code, "service_id": service_id})
            http_response = await common_https.CommonHttps.make_request(url=url, method="GET", headers=None, body=None)
            reliability_details = json.loads(http_response.body)

            logger.info("0005", "Received reliability details from Spine route lookup service for {org_code} & "
                                "{service_id}. {reliability_details}",
                        {"org_code": org_code, "service_id": service_id, "reliability_details": reliability_details})
            return reliability_details
        except Exception as e:
            logger.error("0006",
                         "Couldn't obtain reliability details from Spine route lookup service for {org_code} & "
                         "{service_id}. {exception}", {"org_code": org_code, "service_id": service_id, "exception": e})
            raise e

    def _build_request_url(self, path: str, org_code: str, service_id: str) -> str:
        return self.url + "/" + path + "?org-code=" + org_code + "&service-id=" + service_id
