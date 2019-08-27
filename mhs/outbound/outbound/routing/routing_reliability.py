import json
from typing import Dict

from comms import common_https
from utilities import integration_adaptors_logger as log

ROUTING_PATH = "routing"
RELIABILITY_PATH = "reliability"

logger = log.IntegrationAdaptorsLogger("MHS_ROUTING_RELIABILITY")


class RoutingAndReliability:
    """A tool that allows the routing and reliability information for a remote MHS to be retrieved."""

    def __init__(self, spine_route_lookup_url: str):
        """Initialise a new RoutingAndReliability instance.

        :param spine_route_lookup_url: The URL to make requests to the Spine Route Lookup service on. e.g.
        http://example.com. This URL should not contain path or query parameter parts.
        """
        self.url = spine_route_lookup_url

    async def get_end_point(self, org_code: str, service_id: str) -> Dict:
        """Get the endpoint of the MHS registered for the specified org code and service ID.

        :param org_code:
        :param service_id:
        :return: A dictionary containing the end point information.
        """
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

    async def get_reliability(self, org_code: str, service_id: str) -> Dict:
        """Get the reliability information for the MHS registered for the specified org code and service ID.

        :param org_code:
        :param service_id:
        :return: A dictionary containing the reliability information.
        """
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
