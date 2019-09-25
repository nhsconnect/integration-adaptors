from typing import Dict, Tuple, List, AnyStr
from xml.etree.ElementTree import Element

from defusedxml import ElementTree as ET

from mhs_common.messages.ebxml_envelope import NAMESPACES as NS, EBXML_NAMESPACE as EBXML_PREFIX

ERROR_LIST = 'ErrorList'
ERROR = 'Error'
ERR_CODE_CTX = 'codeContext'
ERR_CODE = 'errorCode'
ERR_SEVERITY = 'severity'
ERR_DESC = 'Description'


class EbxmlErrorEnvelope:
    def __init__(self, errors: List[Dict[AnyStr, str]]):
        """
        Constructor method creates ebXML envelope containing provided list of errors

        >>> errors = [{
        >>>     ERR_CODE_CTX: 'CodeContext',
        >>>     ERR_CODE: 'Code',
        >>>     ERR_SEVERITY: 'Error',
        >>>     ERR_DESC: 'Describe me!'
        >>> }]
        >>> ebxml_error_msg = EbxmlErrorEnvelope(errors)

        :param errors: List of dictionaries describing error occurred
        """
        self.errors = errors

    def serialize(self) -> Tuple[AnyStr, Dict[AnyStr, AnyStr], AnyStr]:
        raise NotImplementedError

    @classmethod
    def _from_parsed(cls, parsed_message: Element):
        attrib_fields = [ERR_CODE_CTX, ERR_CODE, ERR_SEVERITY]
        tag_fields = [ERR_DESC]

        errors = []
        for error in parsed_message.findall(f'*/{EBXML_PREFIX}:{ERROR_LIST}/{EBXML_PREFIX}:{ERROR}', NS):
            att = {i: error.attrib['{}{}'.format('{' + NS[EBXML_PREFIX] + '}', i)] for i in attrib_fields}
            tag = {i: error.find(f'{EBXML_PREFIX}:{i}', NS).text for i in tag_fields}
            errors.append({**att, **tag})

        return EbxmlErrorEnvelope(errors)

    @classmethod
    def from_string(cls, message: AnyStr):
        parsed_message: Element = ET.fromstring(message)
        return EbxmlErrorEnvelope._from_parsed(parsed_message)

    @staticmethod
    def is_ebxml_error(parsed: Element) -> bool:
        return False if not parsed or parsed.find(f'*/{EBXML_PREFIX}:{ERROR_LIST}', NS) is None else True
