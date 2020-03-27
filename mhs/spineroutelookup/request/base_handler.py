import tornado.web

from request.tracking_ids_headers_reader import read_tracking_id_headers
from lookup import routing_reliability


class BaseHandler(tornado.web.RequestHandler):
    """A base handler for spine route lookup"""

    def initialize(self, routing: routing_reliability.RoutingAndReliability) -> None:
        """Initialise this request handler with the provided configuration values.

        :param routing: The routing and reliability component to use to look up values in SDS.
        """
        self.routing = routing
        read_tracking_id_headers(self.request.headers)
