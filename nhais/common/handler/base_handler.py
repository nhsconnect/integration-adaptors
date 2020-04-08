from typing import Any, Dict

import tornado.web
import utilities.message_utilities as message_utilities
import utilities.integration_adaptors_logger as log
from comms.http_headers import HttpHeaders

logger = log.IntegrationAdaptorsLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    """A base Tornado request handler with common functionality used by handlers in MHS outbound and MHS inbound."""

    def initialize(self):
        """Initialise this request handler with the provided dependencies.

        :param workflows: The workflows to use to send messages.
        :param config_manager: The object that can be used to obtain configuration details.
        """






