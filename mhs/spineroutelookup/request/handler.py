import tornado.web
from utilities import timing, integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('SPINE_ROUTE_LOOKUP_REQUEST_HANDLER')


class RoutingDirectoryRequestHandler(tornado.web.RequestHandler):
    @timing.time_request
    async def get(self):
        logger.info('001', 'This Spine Route Lookup server is yet to be implemented.')
        self.write("This Spine Route Lookup server is yet to be implemented.")
