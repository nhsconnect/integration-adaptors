from typing import Tuple, AnyStr, Dict, Optional
from xml.etree import ElementTree as ET

from utilities.integration_adaptors_logger import IntegrationAdaptorsLogger

from mhs_common.messages.ebxml_error_envelope import EbxmlErrorEnvelope

logger = IntegrationAdaptorsLogger('EBXML_ERROR_HANDLER')

ERROR_RESPONSE_DEFAULTS = {
    'errorType': 'ebxml_error'
}


def handle_ebxml_error(code: int, headers: Dict, body: str) -> Tuple[int, Optional[AnyStr]]:
    """
    Analyzes response from NHS and returns result of interpretation to external client

    :param code: HTTP response code
    :param headers: HTTP response headers
    :param body: HTTP response body
    :return: Response to external client represented as HTTP status code and body
    """

    if code != 200 or not body:
        logger.warning('0001', 'Not HTTP 200 response. {Code} {Body}', {'Code': code, 'Body': body})
        return code, body

    if 'Content-Type' not in headers:
        raise ValueError('No Content-Type header in Spine response, response cannot be handled!')

    if headers['Content-Type'] != 'text/xml':
        raise ValueError('Unexpected Content-Type {}!'.format(headers['Content-Type']))

    parsed_body = ET.fromstring(body)

    if not EbxmlErrorEnvelope.is_ebxml_error(parsed_body):
        logger.info('0002', 'Not ebXML error.')
        return code, body

    ebxml_error_envelope: EbxmlErrorEnvelope = EbxmlErrorEnvelope.from_string(body)

    errors_text = ''
    for idx, error_fields in enumerate(ebxml_error_envelope.errors):
        all_fields = {**error_fields, **ERROR_RESPONSE_DEFAULTS}
        errors_text += '{}: {}\n'.format(idx, ' '.join([f'{k}={v}' for k, v in all_fields.items()]))
        logger.error('0002',
                     'ebXML error returned: {}'.format(' '.join(f'{{{i}}}' for i in all_fields.keys())),
                     all_fields)

    return code, f'Error(s) received from Spine. Contact system administrator.\n{errors_text}'
