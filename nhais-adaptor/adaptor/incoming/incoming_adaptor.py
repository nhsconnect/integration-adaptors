from typing import List, Tuple

import edifact.incoming.parser.deserialiser as deserialiser
from adaptor.incoming.operation_definition_adaptor import OperationDefinitionAdaptor


class IncomingAdaptor:
    def __init__(self, reference_dict):
        self.reference_dict = reference_dict

    def covert_to_fhir(self, edifact_payload) -> List[Tuple[str, str, str]]:
        lines = edifact_payload.split("'\n")
        interchange = deserialiser.convert(lines)

        incoming_adaptor = OperationDefinitionAdaptor(self.reference_dict)
        return incoming_adaptor.create_operation_definition(interchange)
