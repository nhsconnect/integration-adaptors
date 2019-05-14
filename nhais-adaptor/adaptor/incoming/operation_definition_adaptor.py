from datetime import datetime
from typing import List, Tuple

from fhirclient.models.operationdefinition import OperationDefinition

import adaptor.fhir_helpers.fhir_creators as creators
from edifact.incoming.models.interchange import Interchange


class OperationDefinitionAdaptor:

    def __init__(self, reference_dict):
        self.reference_dict = reference_dict

    @staticmethod
    def format_date_time(edifact_date_time):
        """
        format the edifact date time to a fhir format
        :param edifact_date_time: The incoming date time stamp from the interchange header
        :return: The formatted date time stamp
        """
        current_format = "%y%m%d:%H%M"
        desired_format = "%Y-%m-%d %H:%M"
        formatted_date = datetime.strptime(edifact_date_time, current_format).strftime(desired_format)
        return formatted_date

    def create_operation_definition(self, interchange: Interchange) -> List[Tuple[str, str, OperationDefinition]]:
        """
        Create a fhir operation definition from the incoming interchange
        :param interchange:
        :return: a List of transaction_numbers, recipients and generated fhir operation definitions
        """
        sender = interchange.header.sender
        recipient = interchange.header.recipient
        formatted_date_time = self.format_date_time(interchange.header.date_time)
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
                op_defs.append((transaction_number, recipient, op_def))

        return op_defs
