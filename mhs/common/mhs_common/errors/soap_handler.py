import json

from typing import Dict, AnyStr, Tuple

from defusedxml import ElementTree
import utilities.integration_adaptors_logger as log
from comms.http_headers import HttpHeaders

from mhs_common.messages.soap_fault_envelope import SOAPFault

logger = log.IntegrationAdaptorsLogger(__name__)

ERROR_RESPONSE_DEFAULTS = {
    'errorType': 'soap_fault'
}


def handle_soap_error(code: int, headers: Dict, body: AnyStr) -> Tuple[int, AnyStr, list]:
    """
    Analyzes response from NHS which works in as web service mode
    and returns result of interpretation to external client

    :param code: HTTP response code
    :param headers: HTTP response headers
    :param body: HTTP response body
    :return: Response to external client represented as HTTP status code and body
    """
    soap_fault_codes = []

    if code != 500:
        logger.warning('Not HTTP 500 response. {Code} {Body}', fparams={'Code': code, 'Body': body})
        return code, body, soap_fault_codes

    if HttpHeaders.CONTENT_TYPE not in headers:
        raise ValueError('No Content-Type header in Spine response, response cannot be handled!')

    if headers[HttpHeaders.CONTENT_TYPE] != 'text/xml':
        raise ValueError('Unexpected Content-Type {}!'.format(headers['Content-Type']))

    try:
        parsed_body = ElementTree.fromstring(body)
    except ElementTree.ParseError:
        raise ValueError('Unable to parse response body')

    assert SOAPFault.is_soap_fault(parsed_body), 'Not SOAP Fault response!'
    fault: SOAPFault = SOAPFault.from_parsed(headers, parsed_body)

    error_data_response = {'error_message': 'Error(s) received from Spine. Contact system administrator.',
                           'process_key': 'SOAP_ERROR_HANDLER0002',
                           'errors': []}

    for idx, error_fields in enumerate(fault.error_list):
        all_fields = {**error_fields, **ERROR_RESPONSE_DEFAULTS}
        if all_fields.get('errorCode'):
            soap_fault_codes.append(int(all_fields['errorCode']))
        error_data_response['errors'].append(all_fields)
        logger.error('SOAP Fault returned: {}'.format(' '.join(f'{{{i}}}' for i in all_fields.keys())),
                     fparams=all_fields)

    return 500, json.dumps(error_data_response), soap_fault_codes
