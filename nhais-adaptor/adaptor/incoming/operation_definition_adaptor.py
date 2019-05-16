from typing import List, Tuple

import adaptor.fhir_helpers.fhir_creators as creators
import adaptor.incoming.common.date_formatter as date_formatter
from edifact.incoming.models.interchange import Interchange


class OperationDefinitionAdaptor:

    def __init__(self, reference_dict):
        self.reference_dict = reference_dict

    def create_operation_definition(self, interchange: Interchange) -> List[Tuple[str, str, str]]:
        """
        Create a fhir operation definition from the incoming interchange
        :param interchange:
        :return: a List of transaction_numbers, recipients and generated fhir operation definition json payloads
        """
        sender = interchange.header.sender
        recipient = interchange.header.recipient
        formatted_date_time = date_formatter.format_date_time(interchange.header.date_time)
        messages = interchange.msgs

        op_defs = []

        for message in messages:
            ref_number = message.message_beginning.reference_number

            for transaction in message.transactions:
                transaction_number = transaction.transaction_registration.transaction_number

                parameters = [
                    creators.create_parameter_with_binding("senderCypher", sender, "out"),
                    creators.create_parameter_with_binding("recipientCypher", recipient, "out"),
                    creators.create_parameter_with_binding("transactionNumber", transaction_number, "out")
                ]

                if transaction.transaction_patient:
                    nhs_number = transaction.transaction_patient.nhs_number
                    parameters.append(
                        creators.create_parameter_with_binding("nhsNumber", nhs_number, "out")
                    )

                op_def = creators.create_operation_definition(name=self.reference_dict[ref_number]["name"],
                                                              code=self.reference_dict[ref_number]["code"],
                                                              date_time=formatted_date_time, parameters=parameters)
                op_defs.append((transaction_number, recipient, op_def.as_json()))

        return op_defs
