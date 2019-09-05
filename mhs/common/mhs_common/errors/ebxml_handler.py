from typing import Tuple, AnyStr, Dict

from utilities.integration_adaptors_logger import IntegrationAdaptorsLogger

logger = IntegrationAdaptorsLogger('EBXML_ERROR_HANDLER')


def handle_ebxml_error(code: int, headers: Dict, body: AnyStr) -> Tuple[int, AnyStr]:
    if code != 200:
        logger.warning('0001', 'Not HTTP 200 response. {Code} {Body}', {'Code': code, 'Body': body})
        return code, body

    assert 'Content-Type' in headers, 'No Content-Type header in Spine response, response cannot be handled!'
    assert headers['Content-Type'] == 'text/xml', 'Unexpected Content-Type {}!'.format(headers['Content-Type'])

    parsed_body = ElementTree.fromstring(body)


    pass
