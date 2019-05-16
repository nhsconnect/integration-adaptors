from typing import Tuple
from fhirclient.models.operationdefinition import OperationDefinition

from adaptor.outgoing.interchange_adaptor import InterchangeAdaptor


class OutgoingAdaptor:
    def __init__(self, operation_dict):
        self.operation_dict = operation_dict

    def convert_to_edifact(self, fhir_json_payload) -> Tuple[str, str, str, str]:
        op_def = OperationDefinition(fhir_json_payload)

        adaptor = InterchangeAdaptor(operation_dict=self.operation_dict)
        return adaptor.create_interchange(fhir_operation=op_def)
