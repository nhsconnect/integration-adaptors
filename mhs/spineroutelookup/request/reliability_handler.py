from request.base_handler import BaseHandler
from utilities import timing, integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


class ReliabilityRequestHandler(BaseHandler):
    """A handler for requests to obtain reliability information."""

    @timing.time_request
    async def get(self):
        org_code = self.get_query_argument("org-code")
        service_id = self.get_query_argument("service-id")

        logger.info("Looking up reliability information. {org_code}, {service_id}",
                    fparams={"org_code": org_code, "service_id": service_id})
        reliability_info = await self.routing.get_reliability(org_code, service_id)
        logger.info("Obtained reliability information. {reliability_information}",
                    fparams={"reliability_information": reliability_info})

        self.write(reliability_info)
