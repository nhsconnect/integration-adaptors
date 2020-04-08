
from comms.http_headers import HttpHeaders
from utilities import mdc
from common.handler import base_handler

from utilities import integration_adaptors_logger as log, message_utilities, timing

logger = log.IntegrationAdaptorsLogger(__name__)


class SynchronousHandler(base_handler.BaseHandler):

    @timing.time_request
    async def post(self):
        test_id = self._extract_test_id()
        new_id = test_id

    def _extract_test_id(self):
        message_id = self.request.headers.get(HttpHeaders.TEST_ID, None)
        if not message_id:
            message_id = message_utilities.MessageUtilities.get_uuid()
            mdc.message_id.set(message_id)
            logger.info("Didn't receive message id in incoming request from supplier, so have generated a new one.")
        else:
            mdc.message_id.set(message_id)
            logger.info('Found message id on incoming request.')
        return message_id