from typing import Tuple

from fhirclient.models.operationdefinition import OperationDefinition

import adaptor.fhir_helpers.fhir_finders as finders
from edifact.outgoing.models.interchange import Interchange
from edifact.outgoing.models.message import Messages
from adaptor.fhir_helpers.fhir_creators import ParameterName
import adaptor.outgoing.common.common_adaptor as common_adaptor
import adaptor.outgoing.common.date_formatter as date_formatter


class InterchangeAdaptor:

    def __init__(self, operation_dict):
        self.operation_dict = operation_dict

    def create_interchange(self, fhir_operation: OperationDefinition) -> Tuple[str, str, str, str]:
        """
        Create the edifact interchange from the fhir operation definition
        :param fhir_operation: The operation definition payload
        :return: a tuple consisting of the sender cypher, recipient cypher, interchange sequence number
        and the generated edifact interchange.
        """
        interchange_sequence_number = finders.get_parameter_value(fhir_operation,
                                                                  parameter_name=ParameterName.INTERCHANGE_SEQ_NO)
        sender_cypher = finders.get_parameter_value(fhir_operation, parameter_name=ParameterName.SENDER_CYPHER)
        nhais_cypher = finders.get_parameter_value(fhir_operation, parameter_name=ParameterName.NHAIS_CYPHER)
        recipient = common_adaptor.generate_recipient_from(nhais_cypher)
        formatted_date_time = date_formatter.format_date(date_time=fhir_operation.date.as_json())

        message_adaptor = self.operation_dict[fhir_operation.name]["messageAdaptor"](fhir_operation)

        messages = Messages(messages=[message_adaptor.create_message()])

        interchange = Interchange(sender=sender_cypher, recipient=recipient,
                                  sequence_number=interchange_sequence_number,
                                  date_time=formatted_date_time, messages=messages)

        edifact_interchange = (sender_cypher, recipient, interchange_sequence_number, interchange.to_edifact())

        return edifact_interchange
