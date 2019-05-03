from edifact.incoming.models.interchange import Interchange
from edifact.incoming.models.message import MessageSegment
from fhirclient.models.operationdefinition import OperationDefinition
import adaptor.fhir_helpers.fhir_creators as creators
from datetime import datetime


def format_date_time(edifact_date_time):
    current_format = "%y%m%d:%H%M"
    desired_format = "%Y-%m-%d %H:%M"
    formatted_date = datetime.strptime(edifact_date_time, current_format).strftime(desired_format)
    return formatted_date


def extract_sender_value(interchange):
    return interchange.header.sender


def extract_recipient_value(interchange):
    return interchange.header.recipient


def extract_transaction_number(interchange):
    return interchange.msgs[0].message_registration.transaction_number


def extract_reference_number(message):
    return message.message_beginning.reference_number


def create_operation_definition(interchange: Interchange) -> OperationDefinition:
    """
    Create a fhir operation definition from the incoming interchange
    :param interchange: The incoming interchange
    :return: OperationDefinition:
    """

    response_dict = {
        "F4": {
            "name": "Response-RegisterPatient-Approval",
            "code": "gpc.registerpatient.approval",
            "parameters": {
                "senderCypher": extract_sender_value,
                "recipientCypher": extract_recipient_value,
                "transactionNumber": extract_transaction_number
            }
        }
    }

    message: MessageSegment = interchange.msgs[0]

    ref_number = extract_reference_number(message)

    formatted_date_time = format_date_time(interchange.header.date_time)

    parameters = []
    for (key, extract_fn) in response_dict[ref_number]["parameters"].items():
        extracted_value = extract_fn(interchange)
        param = creators.create_parameter_with_binding(key, extracted_value, "out")
        parameters.append(param)

    op_def = creators.create_operation_definition(name=response_dict[ref_number]["name"],
                                                  code=response_dict[ref_number]["code"],
                                                  date_time=formatted_date_time,
                                                  contained=[],
                                                  parameters=parameters)

    return op_def
