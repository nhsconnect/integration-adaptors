import tornado.web
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    """A base Tornado request handler with common functionality used by handler."""

    def initialize(self):
        """Initialise this request handler with the provided dependencies.
        """






