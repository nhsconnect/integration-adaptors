from tornado.httputil import HTTPHeaders

from comms.http_headers import HttpHeaders
from utilities import message_utilities, mdc, integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


def read_tracking_id_headers(headers: HTTPHeaders):
    _extract_correlation_id(headers)
    _extract_interaction_id(headers)
    _extract_message_id(headers)
    _extract_inbound_message_id(headers)


def _extract_correlation_id(headers: HTTPHeaders):
    correlation_id = headers.get(HttpHeaders.CORRELATION_ID, None)
    if not correlation_id:
        correlation_id = message_utilities.get_uuid()
        logger.info("Didn't receive correlation id in incoming request from supplier, so have generated a new one.")
    mdc.correlation_id.set(correlation_id)


def _extract_message_id(headers: HTTPHeaders):
    message_id = headers.get(HttpHeaders.MESSAGE_ID, None)
    if message_id:
        mdc.message_id.set(message_id)
        logger.info('Found message id on incoming request.')


def _extract_interaction_id(headers: HTTPHeaders):
    interaction_id = headers.get(HttpHeaders.INTERACTION_ID, None)
    if interaction_id:
        mdc.interaction_id.set(interaction_id)
        logger.info('Found interaction id on incoming request.')


def _extract_inbound_message_id(headers: HTTPHeaders):
    inbound_message_id = headers.get(HttpHeaders.INBOUND_MESSAGE_ID, None)
    if inbound_message_id:
        mdc.interaction_id.set(inbound_message_id)
        logger.info('Found inbound message id on incoming request.')