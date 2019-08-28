import tornado.web
from utilities import timing, integration_adaptors_logger as log

from lookup import routing_reliability

logger = log.IntegrationAdaptorsLogger('SPINE_ROUTE_LOOKUP_ROUTING_RELIABILITY_REQUEST_HANDLER')


class RoutingReliabilityRequestHandler(tornado.web.RequestHandler):
    """A handler for requests to obtain combined routing and reliability information."""

    def initialize(self, routing: routing_reliability.RoutingAndReliability) -> None:
        """Initialise this request handler with the provided configuration values.

        :param routing: The routing and reliability component to use to look up values in SDS.
        """
        self.routing = routing

    @timing.time_request
    async def get(self):
        org_code = self.get_query_argument("org-code")
        service_id = self.get_query_argument("service-id")

        logger.info("001", "Looking up routing information. {org_code}, {service_id}",
                    {"org_code": org_code, "service_id": service_id})
        routing_info = await self.routing.get_end_point(org_code, service_id)
        logger.info("002", "Obtained routing information. {routing_information}", {"routing_information": routing_info})

        logger.info("003", "Looking up reliability information. {org_code}, {service_id}",
                    {"org_code": org_code, "service_id": service_id})
        reliability_info = await self.routing.get_reliability(org_code, service_id)
        logger.info("004", "Obtained reliability information. {reliability_information}",
                    {"reliability_information": reliability_info})

        combined_info = {**routing_info, **reliability_info}
        logger.info("005", "Combined routing and reliability information. {routing_reliability_information}",
                    {"routing_reliability_information": combined_info})

        self.write(combined_info)
