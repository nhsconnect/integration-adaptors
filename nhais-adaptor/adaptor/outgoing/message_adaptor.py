import adaptor.outgoing.birth.message_birth_adaptor as message_birth_adaptor
from edifact.outgoing.models.message import MessageBeginning
from edifact.outgoing.models.Birth.message_birth import Message
import adaptor.fhir_helpers.fhir_finders as finders
from adaptor.fhir_helpers.fhir_creators import ParameterName, OperationName

operation_dict = {
    OperationName.REGISTER_BIRTH: {
        "refNumber": "G1",
        "registrationDetails": message_birth_adaptor.create_message_segment_registration_details,
        "patientDetails": message_birth_adaptor.create_message_segment_patient_detail
    }
}


def create_message_beginning(fhir_operation):
    """
    Create the beginning of the message
    :return: MessageBeginning
    """
    nhais_id = finders.get_parameter_value(fhir_operation=fhir_operation, parameter_name=ParameterName.NHAIS_CYPHER)

    ref_number = operation_dict[OperationName.REGISTER_BIRTH]["refNumber"]

    msg_bgn = MessageBeginning(party_id=nhais_id, date_time=fhir_operation.date.as_json(), ref_number=ref_number)

    return msg_bgn


def create_message(fhir_operation):
    """
    Create the edifact Message
    :return: Message
    """
    message_sequence_number = finders.get_parameter_value(fhir_operation=fhir_operation,
                                                          parameter_name=ParameterName.MESSAGE_SEQ_NO)

    registration_details = operation_dict[fhir_operation.name]["registrationDetails"](fhir_operation)
    patient_details = operation_dict[fhir_operation.name]["patientDetails"](fhir_operation)
    message = Message(sequence_number=message_sequence_number,
                      message_beginning=create_message_beginning(fhir_operation),
                      message_segment_registration_details=registration_details,
                      message_segment_patient_details=patient_details)

    return message
