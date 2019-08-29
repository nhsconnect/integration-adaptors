""" Module defines a class representing SOAP Fault response from NHS Spine """
from typing import Tuple, Dict, AnyStr, List
from xml.etree import ElementTree

from mhs_common.messages.envelope import Envelope
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
ERR_CODE = f'{NS_NASP}:errorCode'
ERR_SEVERITY = f'{NS_NASP}:severity'
ERR_LOCATION = f'{NS_NASP}:location'
ERR_DESCRIPTION = f'{NS_NASP}:description'
ERR_CODE_CONTEXT = f'{NS_NASP}:codeContext'

ERR_FIELDS = [ERR_CODE, ERR_SEVERITY, ERR_LOCATION, ERR_DESCRIPTION, ERR_CODE_CONTEXT]


def _extract_tag_text(elem: ElementTree.ElementTree, path: AnyStr) -> AnyStr:
    try:
        return elem.find(path, NS).text
    except AttributeError as e:
        # Log error here
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
    def is_soap_fault(parsed_message: ElementTree.ElementTree) -> bool:
        if parsed_message is not None and len(parsed_message.findall(f'*/{SOAP_FAULT}', NS)):
            return True

        return False

    @classmethod
    def from_string(cls, headers: Dict[str, str], message: str) -> Envelope:
        parsed: ElementTree.ElementTree = ElementTree.fromstring(message)

        fault_code = _extract_tag_text(parsed, f'*/{SOAP_FAULT}/{FAULT_CODE}')
        fault_string = _extract_tag_text(parsed, f'*/{SOAP_FAULT}/{FAULT_STRING}')

        error_list = []
        for error in parsed.findall(f'*/{SOAP_FAULT}/{DETAIL}/{ERROR_LIST}/{ERROR}', NS):
            error_list.append({field: error.find(f'./{field}', NS).text for field in ERR_FIELDS})

        return SOAPFault(fault_code, fault_string, error_list)

    def serialize(self) -> Tuple[str, Dict[str, str], str]:
        raise NotImplementedError


MSG = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:crs="http://national.carerecords.nhs.uk/schema/crs/" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing">
  <SOAP:Body>
    <SOAP:Fault>
      <faultcode>SOAP:Server</faultcode>
      <faultstring>Application Exception</faultstring>
      <detail>
        <nasp:errorList xmlns:nasp="http://national.carerecords.nhs.uk/schema/">
          <nasp:error>
            <nasp:codeContext>urn:nhs:names:error:tms</nasp:codeContext>
            <nasp:errorCode>200</nasp:errorCode>
            <nasp:severity>Error</nasp:severity>
            <nasp:location>Not Supported</nasp:location>
            <nasp:description>System failure to process message - default</nasp:description>
          </nasp:error>
        </nasp:errorList>
      </detail>
    </SOAP:Fault>
  </SOAP:Body>
</SOAP:Envelope>
"""

if __name__ == '__main__':
    x = SOAPFault.from_string({}, MSG)

    print(x)
