from typing import Tuple

from fhirclient.models.operationdefinition import OperationDefinition

import adaptor.fhir_helpers.fhir_finders as finders
from edifact.outgoing.models.interchange import Interchange
from edifact.outgoing.models.message import Messages
from adaptor.fhir_helpers.fhir_creators import ParameterName


class InterchangeAdaptor:

    def __init__(self, operation_dict):
        self.operation_dict = operation_dict

    @staticmethod
    def generate_recipient_from(nhais_cypher):
        """
        Generates the recipient cypher. This value can be deduced from the nhais_cypher provided.
        The nhais cypher can be 2 to 3 characters is length.
        If it is 2 characters in length it will append "01" to generate the recipient cypher
        If it is 3 characters in length it will append "1" to generate the recipient cypher
        :param nhais_cypher: The nhais cypher provided. Should be 2-3 characters in length
        :return: The recipient cypher
        """
        recipient = ''
        if len(nhais_cypher) == 3:
            recipient = nhais_cypher + '1'
        elif len(nhais_cypher) == 2:
            recipient = nhais_cypher + "01"
        return recipient

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
        recipient = self.generate_recipient_from(nhais_cypher)

        message_adaptor = self.operation_dict[fhir_operation.name]["messageAdaptor"](fhir_operation)

        messages = Messages(messages=[message_adaptor.create_message()])

        interchange = Interchange(sender=sender_cypher, recipient=recipient,
                                  sequence_number=interchange_sequence_number,
                                  date_time=fhir_operation.date.as_json(), messages=messages)

        edifact_interchange = (sender_cypher, recipient, interchange_sequence_number, interchange.to_edifact())

        return edifact_interchange
