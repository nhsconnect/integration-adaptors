from edifact.incoming.models.interchange import Interchange
import adaptor.fhir_helpers.fhir_creators as creators
from datetime import datetime


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


def create_operation_definition(interchange: Interchange):
    """
    Create a fhir operation definition from the incoming interchange
    :param interchange: The incoming interchange
    :return: OperationDefinition:
    """

    APPROVAL_REFERENCE = "F4"

    response_dict = {
        APPROVAL_REFERENCE: {
            "name": "Response-RegisterPatient-Approval",
            "code": "gpc.registerpatient.approval"
        }
    }

    sender = interchange.header.sender
    recipient = interchange.header.recipient
    formatted_date_time = format_date_time(interchange.header.date_time)
    messages = interchange.msgs

    op_defs = []

    for message in messages:
        ref_number = message.message_beginning.reference_number
        transaction_number = message.message_registration.transaction_number

        parameters = [
            creators.create_parameter_with_binding("senderCypher", sender, "out"),
            creators.create_parameter_with_binding("recipientCypher", recipient, "out"),
            creators.create_parameter_with_binding("transactionNumber", transaction_number, "out")
        ]

        op_def = creators.create_operation_definition(name=response_dict[ref_number]["name"],
                                                      code=response_dict[ref_number]["code"],
                                                      date_time=formatted_date_time,
                                                      contained=[],
                                                      parameters=parameters)
        op_defs.append((transaction_number, recipient, op_def))

    return op_defs
