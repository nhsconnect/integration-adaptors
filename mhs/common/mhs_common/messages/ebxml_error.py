from enum import Enum
from typing import Dict, Tuple, List, AnyStr, Any
from xml.etree import ElementTree as ET

from mhs_common.messages.ebxml_envelope import EbxmlEnvelope, NAMESPACES as NS, EBXML_NAMESPACE as EBXML_PREFIX
from mhs_common.messages.envelope import Envelope


ERROR_LIST = 'ErrorList'
ERROR = 'Error'
ERR_CODE_CTX = 'codeContext'
ERR_CODE = 'errorCode'
ERR_SEVERITY = 'severity'
ERR_DESC = 'Description'


class EbxmlError(EbxmlEnvelope):
    def __init__(self, template_file: AnyStr, message_dictionary: Dict[AnyStr, Any]):
        super().__init__(template_file, message_dictionary)

    def serialize(self) -> Tuple[AnyStr, Dict[AnyStr, AnyStr], AnyStr]:
        raise NotImplementedError

    @classmethod
    def from_string(cls, headers: Dict[AnyStr, AnyStr], message: AnyStr) -> Envelope:
        attrib_fields = [ERR_CODE_CTX, ERR_CODE, ERR_SEVERITY]
        tag_fields = [ERR_DESC]

        parsed_message: ET.ElementTree = ET.fromstring(message)

        errors = []
        for error in parsed_message.findall('*/eb:ErrorList/eb:Error', NS):
            att = {i: error.attrib['{}{}'.format('{' + NS[EBXML_PREFIX] + '}', i)] for i in attrib_fields}
            tag = {i: error.find(f'{EBXML_PREFIX}:{i}', NS).text for i in tag_fields}
            errors.append({**att, **tag})


MSG = """<?xml version="1.0" encoding="utf-8"?>
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
"""

if __name__ == '__main__':
    EbxmlError.from_string({}, MSG)
    pass