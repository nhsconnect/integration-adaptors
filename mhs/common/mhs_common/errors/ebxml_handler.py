from typing import Tuple, AnyStr, Dict, Optional

from defusedxml import ElementTree as ET
from utilities.integration_adaptors_logger import IntegrationAdaptorsLogger

from mhs_common.messages.ebxml_error_envelope import EbxmlErrorEnvelope

logger = IntegrationAdaptorsLogger('EBXML_ERROR_HANDLER')

ERROR_RESPONSE_DEFAULTS = {
    'errorType': 'ebxml_error'
}


def handle_ebxml_error(code: int, headers: Dict, body: AnyStr) -> Tuple[int, Optional[AnyStr]]:
    """
    Analyzes response from MHS and returns result of interpretation to external client
    Normally MHS doesn't return HTTP code 500 in case of ebXML error occurred. HTTP 200 will be returned instead
    with content-type text/xml and body represented as XML and having following structure:

    <?xml version="1.0" encoding="utf-8"?>
    <SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/" xmlns:eb="http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd">
        <SOAP:Header>
            <eb:MessageHeader SOAP:mustUnderstand="1" eb:version="2.0">
                <eb:From>
                    <eb:PartyId eb:type="urn:nhs:names:partyType:ocs+serviceInstance">YEA-801248</eb:PartyId>
                </eb:From>
                <eb:To>
                    <eb:PartyId eb:type="urn:nhs:names:partyType:ocs+serviceInstance">RHM-810292</eb:PartyId>
                </eb:To>
                <eb:CPAId>S2001919A2011852</eb:CPAId>
                <eb:ConversationId>19D02203-3CBE-11E3-9D44-9D223D2F4DB0</eb:ConversationId>
                <eb:Service>urn:oasis:names:tc:ebxml-msg:service</eb:Service>
                <eb:Action>MessageError</eb:Action>
                <eb:MessageData>
                    <eb:MessageId>97111C1C-48B8-B2FA-DE13-B64B2ADEB391</eb:MessageId>
                    <eb:Timestamp>2013-10-24T15:08:07</eb:Timestamp>
                    <eb:RefToMessageId>19D02203-3CBE-11E3-9D44-9D223D2F4DB0</eb:RefToMessageId>
                </eb:MessageData>
            </eb:MessageHeader>
            <eb:ErrorList SOAP:mustUnderstand="1" eb:highestSeverity="Error" eb:version="2.0">
                <eb:Error eb:codeContext="urn:oasis:names:tc:ebxml-msg:service:errors" eb:errorCode="ValueNotRecognized" eb:severity="Error">
                    <eb:Description xml:lang="en-GB">501319:Unknown eb:CPAId</eb:Description>
                </eb:Error>
            </eb:ErrorList>
        </SOAP:Header>
        <SOAP:Body/>
    </SOAP:Envelope>

    Function checks for HTTP code 200, content-type text/xml and body for the structure as above.
    In case there is not HTTP code 200 passed in, `code` and `body` will be returned back.
    In case HTTP code that is not 2xx is passed in, a `ValueError` exception will be raised.
    In case body isn't structured as ebXML error message passed `code` and `body` will be returned back.
    In case content-type is not presented or is not text/xml `ValueError` exception should be raised.
    In case the response actually is ebXML error all the error details like severity, description, error code and
    error context will be logged according to logging policy with `errorType` equal to `ebxml_error`.

    :param code: HTTP response code
    :param headers: HTTP response headers
    :param body: HTTP response body
    :return: Response to external client represented as HTTP status code and body
    """

    if code != 200:
        if code // 100 == 2:  # If code is 2xx
            logger.info('0001', "HTTP {Code} success response code received. So can assume this isn't an ebXML error "
                                "as they are HTTP 200.", {'Code': code})
            return code, body
        logger.error('0002', 'Non-HTTP 2xx response code received: {Code} . It is likely that there is a bug in the '
                             'code.', {'Code': code})
        raise ValueError(f'Non-HTTP-2xx code passed to ebxml_handler function: {code}')

    if not body:
        logger.info('0003',
                    "HTTP 200 success response received with empty body, so can assume this isn't an ebXML error.")
        return code, body

    if 'Content-Type' not in headers:
        raise ValueError('No Content-Type header in Spine response, response cannot be handled!')

    if headers['Content-Type'] != 'text/xml':
        raise ValueError('Unexpected Content-Type {}!'.format(headers['Content-Type']))

    parsed_body = ET.fromstring(body)

    if not EbxmlErrorEnvelope.is_ebxml_error(parsed_body):
        logger.info('0004', 'Not ebXML error.')
        return code, body

    ebxml_error_envelope: EbxmlErrorEnvelope = EbxmlErrorEnvelope.from_string(body)

    errors_text = ''
    for idx, error_fields in enumerate(ebxml_error_envelope.errors):
        all_fields = {**error_fields, **ERROR_RESPONSE_DEFAULTS}
        errors_text += '{}: {}\n'.format(idx, ' '.join([f'{k}={v}' for k, v in all_fields.items()]))
        logger.error('0005',
                     'ebXML error returned: {}'.format(' '.join(f'{{{i}}}' for i in all_fields.keys())),
                     all_fields)

    return 500, f'Error(s) received from Spine. Contact system administrator.\n{errors_text}'
