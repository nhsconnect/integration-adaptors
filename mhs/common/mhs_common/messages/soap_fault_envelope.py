""" Module defines a class representing SOAP Fault response from NHS Spine """
from typing import Tuple, Dict, AnyStr, List
from xml.etree.ElementTree import Element

from defusedxml import ElementTree
import utilities.integration_adaptors_logger as log

from mhs_common.messages.soap_envelope import SoapEnvelope

NS_SOAP = 'SOAP'
NS_SOAP_ENV = 'SOAP-ENV'
NS_CRS = 'crs'
NS_WSA = 'wsa'
NS_NASP = 'nasp'

NS = {
    NS_SOAP: 'http://schemas.xmlsoap.org/soap/envelope/',
    NS_SOAP_ENV: 'http://schemas.xmlsoap.org/soap/envelope/',
    NS_CRS: 'http://national.carerecords.nhs.uk/schema/crs/',
    NS_WSA: 'http://schemas.xmlsoap.org/ws/2004/08/addressing',
    NS_NASP: 'http://national.carerecords.nhs.uk/schema/'
}

SOAP_FAULT = f'{NS_SOAP}:Fault'
FAULT_CODE = 'faultcode'
FAULT_STRING = 'faultstring'
DETAIL = 'detail'
ERROR_LIST = f'{NS_NASP}:errorList'
ERROR = f'{NS_NASP}:error'

ERR_CODE = 'errorCode'
ERR_SEVERITY = 'severity'
ERR_LOCATION = 'location'
ERR_DESCRIPTION = 'description'
ERR_CODE_CONTEXT = 'codeContext'

ERR_FIELDS = [ERR_CODE, ERR_SEVERITY, ERR_LOCATION, ERR_DESCRIPTION, ERR_CODE_CONTEXT]

logger = log.IntegrationAdaptorsLogger(__name__)

SYSTEM_FAILURE_TO_PROCESS_MESSAGE_ERROR_CODE = 200
ROUTING_DELIVERY_FAILURE_ERROR_CODE = 206
FAILURE_STORING_VARIABLE_IN_MEMO = 208

SOAP_ERRORS_TO_RETRY = [SYSTEM_FAILURE_TO_PROCESS_MESSAGE_ERROR_CODE,
                        ROUTING_DELIVERY_FAILURE_ERROR_CODE,
                        FAILURE_STORING_VARIABLE_IN_MEMO]


def _extract_tag_text(elem: ElementTree, path: AnyStr) -> AnyStr:
    try:
        return elem.find(path, NS).text
    except AttributeError as e:
        logger.error('Error while extracting value of {path}', fparams={'path': path})
        raise e


class SOAPFault(SoapEnvelope):
    def __init__(self,
                 fault_code: AnyStr,
                 fault_string: AnyStr,
                 error_list: List[Dict[AnyStr, AnyStr]]):
        self.fault_code = fault_code
        self.fault_string = fault_string
        self.error_list = error_list

    @staticmethod
    def is_soap_fault(parsed_message: Element) -> bool:
        if parsed_message is not None and len(parsed_message.findall(f'*/{SOAP_FAULT}', NS)):
            return True

        return False

    @classmethod
    def from_string(cls, headers: Dict[str, str], message: str):
        parsed: Element = ElementTree.fromstring(message)
        return SOAPFault.from_parsed(headers, parsed)

    @classmethod
    def from_parsed(cls, headers: Dict[str, str], parsed: Element):
        fault_code = _extract_tag_text(parsed, f'*/{SOAP_FAULT}/{FAULT_CODE}')
        fault_string = _extract_tag_text(parsed, f'*/{SOAP_FAULT}/{FAULT_STRING}')

        error_list = []
        for error in parsed.findall(f'*/{SOAP_FAULT}/{DETAIL}/{ERROR_LIST}/{ERROR}', NS):
            error_list.append({field: error.find(f'./{NS_NASP}:{field}', NS).text for field in ERR_FIELDS})

        return SOAPFault(fault_code, fault_string, error_list)

    def serialize(self) -> Tuple[str, Dict[str, str], str]:
        raise NotImplementedError

    @staticmethod
    def is_soap_fault_retriable(soap_fault_codes):
        # return True only if ALL error codes are retriable
        for soap_fault_code in soap_fault_codes:
            if soap_fault_code not in SOAP_ERRORS_TO_RETRY:
                return False
        return True
