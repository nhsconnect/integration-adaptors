from typing import Dict, AnyStr, Tuple
from xml.etree import ElementTree
from utilities.integration_adaptors_logger import IntegrationAdaptorsLogger
from mhs_common.messages.soap_fault import SOAPFault
from mhs_common.errors import ERROR_RESPONSE_DEFAULTS

logger = IntegrationAdaptorsLogger('SOAP_ERROR_HANDLER')


def handle_soap_error(code: int, headers: Dict, body: AnyStr) -> Tuple[int, AnyStr]:
    """
    Analyzes response from NHS which works in as web service mode
    and returns result of interpretation to external client

    :param code: HTTP response code
    :param headers: HTTP response headers
    :param body: HTTP response body
    :return: Response to external client represented as HTTP status code and body
    """
    if code != 500:
        logger.warning('0001', 'Not HTTP 500 response. {Code} {Body}', {'Code': code, 'Body': body})
        return code, body

    if 'Content-Type' not in headers:
        raise ValueError('No Content-Type header in Spine response, response cannot be handled!')

    if headers['Content-Type'] == 'text/xml':
        raise ValueError('Unexpected Content-Type {}!'.format(headers['Content-Type']))

    parsed_body = ElementTree.fromstring(body)

    assert SOAPFault.is_soap_fault(parsed_body), 'Not SOAP Fault response!'
    fault: SOAPFault = SOAPFault.from_parsed(headers, parsed_body)

    errors_text = ''
    for idx, error_fields in enumerate(fault.error_list):
        all_fields = {**error_fields, **ERROR_RESPONSE_DEFAULTS}
        errors_text += '{}: {}\n'.format(idx, ' '.join([f'{k}={v}' for k, v in all_fields.items()]))
        logger.error('0002',
                     'SOAP Fault returned: {}'.format(' '.join(['{' + f'{i}' + '}' for i in all_fields.keys()])),
                     all_fields)

    return code, f'Error(s) received from Spine. Contact system administrator.\n{errors_text}'
