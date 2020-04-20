from utilities import integration_adaptors_logger as log
import re
from xml.etree import ElementTree

logger = log.IntegrationAdaptorsLogger(__name__)

MESSAGE_ID_EXPRESSION = re.compile('(<eb:MessageId>(?P<messageId>.+)</eb:MessageId>)')


def body_contains_message_id(body: str, message_id: str) -> bool:
    """
    Returns true if the SOAP MessageID section contains the message if provided
    :param body: the SOAP request as a string
    :param message_id: the message_id expected
    :return: true if message_id was found in the SOAP request
    """
    logger.info(f"Attempting to parse body: {body}")
    try:
        root_xml = ElementTree.fromstring(body)
    except ElementTree.ParseError:
        logger.info('Unable to parse XML: some request types are not parsed as XML')
        return False
    else:
        element_matching_xpath = root_xml.find('.//wsa:MessageID', namespaces={'wsa': 'http://schemas.xmlsoap.org/ws/2004/08/addressing'})

        if element_matching_xpath is None:
            logger.info(f'message id {message_id} not found')
            return False

        logger.info(f'Element matching xpath found with value: {element_matching_xpath.text}')
        return f'uuid:{message_id}' == element_matching_xpath.text


def ebxml_body_contains_message_id(body: str, message_id: str) -> bool:
    matches = MESSAGE_ID_EXPRESSION.search(body)
    if matches is None or len(matches.groups()) != 2:
        logger.info(f'message id {message_id} not found')
        return False

    found_message_id = matches.group('messageId')
    logger.info(f'Element matching MessageId found with value: {found_message_id}')
    return message_id == found_message_id
