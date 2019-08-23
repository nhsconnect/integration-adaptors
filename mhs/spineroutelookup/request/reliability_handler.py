import tornado.web
from utilities import timing, integration_adaptors_logger as log

from lookup import routing_reliability

logger = log.IntegrationAdaptorsLogger('SPINE_ROUTE_LOOKUP_RELIABILITY_REQUEST_HANDLER')


class ReliabilityRequestHandler(tornado.web.RequestHandler):
    """A handler for requests to obtain reliability information."""

    def initialize(self, routing: routing_reliability.RoutingAndReliability) -> None:
        """Initialise this request handler with the provided configuration values.

        :param routing: The routing and reliability component to use to look up values in SDS.
        """
        self.routing = routing

    @timing.time_request
    async def get(self):
        org_code = self.get_query_argument("org-code")
        service_id = self.get_query_argument("service-id")

        logger.info("001", "Looking up reliability information. {org_code}, {service_id}",
                    {"org_code": org_code, "service_id": service_id})
        reliability_info = await self.routing.get_reliability(org_code, service_id)
        logger.info("002", "Obtained reliability information. {reliability_information}",
                    {"reliability_information": reliability_info})

        self.write(reliability_info)
