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


class EbxmlErrorEnvelope(EbxmlEnvelope):
    def __init__(self, errors: List[Dict[AnyStr, Any]]):
        super().__init__('ebxml_error', {})
        self.errors = errors

    def serialize(self) -> Tuple[AnyStr, Dict[AnyStr, AnyStr], AnyStr]:
        raise NotImplementedError

    @classmethod
    def from_parsed(cls, headers: Dict[AnyStr, AnyStr], parsed_message: ET.ElementTree):
        attrib_fields = [ERR_CODE_CTX, ERR_CODE, ERR_SEVERITY]
        tag_fields = [ERR_DESC]

        errors = []
        for error in parsed_message.findall(f'*/{EBXML_PREFIX}:{ERROR_LIST}/{EBXML_PREFIX}:{ERROR}', NS):
            att = {i: error.attrib['{}{}'.format('{' + NS[EBXML_PREFIX] + '}', i)] for i in attrib_fields}
            tag = {i: error.find(f'{EBXML_PREFIX}:{i}', NS).text for i in tag_fields}
            errors.append({**att, **tag})

        return EbxmlErrorEnvelope(errors)

    @classmethod
    def from_string(cls, headers: Dict[AnyStr, AnyStr], message: AnyStr) -> Envelope:
        parsed_message: ET.ElementTree = ET.fromstring(message)
        return EbxmlErrorEnvelope.from_parsed(headers, parsed_message)

    @staticmethod
    def is_ebxml_error(parsed: ET.ElementTree) -> bool:
        return False if parsed.find(f'*/{EBXML_PREFIX}:{ERROR_LIST}', NS) is None else True
