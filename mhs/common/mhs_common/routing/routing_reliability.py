import json
from typing import Dict

from comms import common_https
from utilities.mdc import build_tracking_headers
from utilities import integration_adaptors_logger as log, timing

ROUTING_PATH = "routing"
RELIABILITY_PATH = "reliability"

logger = log.IntegrationAdaptorsLogger(__name__)


class RoutingAndReliability:
    """A tool that allows the routing and reliability information for a remote MHS to be retrieved."""

    def __init__(self, spine_route_lookup_url: str, spine_org_code: str, client_cert: str = None,
                 client_key: str = None, ca_certs: str = None, http_proxy_host: str = None,
                 http_proxy_port: int = None):
        """Initialise a new RoutingAndReliability instance.

        :param spine_route_lookup_url: The URL to make requests to the Spine Route Lookup service on. e.g.
        http://example.com. This URL should not contain path or query parameter parts.
        :param spine_org_code The organisation code of the Spine instance this MHS is communicating with.
        :param client_cert: An optional string containing the path of the client certificate file.
        :param client_key: An optional string containing the path of the client private key file.
        :param ca_certs: An optional string containing the path of the certificate authority certificate file.
        :param http_proxy_host The hostname of the HTTP proxy to be used.
        :param http_proxy_port The port of the HTTP proxy to be used.
        """
        self.url = spine_route_lookup_url
        self.spine_org_code = spine_org_code

        self._client_cert = client_cert
        self._client_key = client_key
        self._ca_certs = ca_certs

        self._proxy_host = http_proxy_host
        self._proxy_port = http_proxy_port

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
            logger.info("No org code provided when obtaining endpoint details. Using {spine_org_code}",
                        fparams={"spine_org_code": org_code})

        url = self._build_request_url(ROUTING_PATH, org_code, service_id)

        try:

            logger.info("Requesting endpoint details from Spine route lookup service for {org_code} & {service_id}.",
                        fparams={"org_code": org_code, "service_id": service_id})
            http_response = await common_https.CommonHttps.make_request(url=url, method="GET",
                                                                        headers=build_tracking_headers(),
                                                                        body=None,
                                                                        client_cert=self._client_cert,
                                                                        client_key=self._client_key,
                                                                        ca_certs=self._ca_certs,
                                                                        http_proxy_host=self._proxy_host,
                                                                        http_proxy_port=self._proxy_port)
            endpoint_details = json.loads(http_response.body)

            logger.info("Received endpoint details from Spine route lookup service for {org_code} & "
                        "{service_id}. {endpoint_details}",
                        fparams={"org_code": org_code, "service_id": service_id, "endpoint_details": endpoint_details})
            return endpoint_details
        except Exception:
            logger.exception("Couldn't obtain endpoint details from Spine route lookup service for {org_code} & "
                         "{service_id}.",
                         fparams={"org_code": org_code, "service_id": service_id})
            raise

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
            logger.info("No org code provided when obtaining reliability details. Using {spine_org_code}",
                        fparams={"spine_org_code": org_code})

        url = self._build_request_url(RELIABILITY_PATH, org_code, service_id)

        try:
            logger.info("Requesting reliability details from Spine route lookup service for {org_code} & "
                        "{service_id}.",
                        fparams={"org_code": org_code, "service_id": service_id})
            http_response = await common_https.CommonHttps.make_request(url=url, method="GET",
                                                                        headers=build_tracking_headers(),
                                                                        body=None,
                                                                        client_cert=self._client_cert,
                                                                        client_key=self._client_key,
                                                                        ca_certs=self._ca_certs,
                                                                        http_proxy_host=self._proxy_host,
                                                                        http_proxy_port=self._proxy_port)
            reliability_details = json.loads(http_response.body)

            logger.info("Received reliability details from Spine route lookup service for {org_code} & "
                        "{service_id}. {reliability_details}",
                        fparams={
                            "org_code": org_code,
                            "service_id": service_id,
                            "reliability_details": reliability_details
                        })
            return reliability_details
        except Exception:
            logger.exception("Couldn't obtain reliability details from Spine route lookup service for {org_code} & "
                             "{service_id}.",
                             fparams={"org_code": org_code, "service_id": service_id}, exc_info=True)
            raise

    def _build_request_url(self, path: str, org_code: str, service_id: str) -> str:
        return self.url + "/" + path + "?org-code=" + org_code + "&service-id=" + service_id
