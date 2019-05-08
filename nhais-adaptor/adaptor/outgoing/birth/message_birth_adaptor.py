from fhirclient.models.operationdefinition import OperationDefinition

import adaptor.fhir_helpers.fhir_finders as finders
from adaptor.fhir_helpers.fhir_creators import ResourceType, ParameterName, OperationName
from adaptor.outgoing.common.common_adaptor import create_patient_name, create_patient_address
from edifact.outgoing.models.birth.message_birth import MessageSegmentBirthPatientDetails, \
    MessageSegmentBirthRegistrationDetails

operation_dict = {
    OperationName.REGISTER_BIRTH: {
        "acceptanceCode": "A",
        "acceptanceType": "1",
    }
}


def create_message_segment_patient_detail(fhir_operation: OperationDefinition) -> MessageSegmentBirthPatientDetails:
    """
    Create the message segment patient details for a birth registration from the fhir operation
    :return: MessageSegmentBirthPatientDetails
    """
    gender_map = {'unknown': 0, 'male': 1, 'female': 2, 'other': 9}

    patient = finders.find_resource(fhir_operation, resource_type=ResourceType.PATIENT)

    edi_name = create_patient_name(patient.name[0])

    edi_address = create_patient_address(patient.address[0])

    msg_seg_patient_details = MessageSegmentBirthPatientDetails(id_number=patient.identifier[0].value,
                                                                name=edi_name,
                                                                date_of_birth=patient.birthDate.as_json(),
                                                                gender=gender_map[patient.gender],
                                                                address=edi_address)
    return msg_seg_patient_details


def create_message_segment_registration_details(
        fhir_operation: OperationDefinition) -> MessageSegmentBirthRegistrationDetails:
    """
    Create the message segment registration details for a birth registration from the fhir operation
    :return: MessageSegmentBirthRegistrationDetails
    """

    transaction_number = finders.get_parameter_value(fhir_operation=fhir_operation,
                                                     parameter_name=ParameterName.TRANSACTION_NO)

    acceptance_code = operation_dict[OperationName.REGISTER_BIRTH]["acceptanceCode"]
    acceptance_type = operation_dict[OperationName.REGISTER_BIRTH]["acceptanceType"]

    practitioner_details = finders.find_resource(fhir_operation=fhir_operation,
                                                 resource_type=ResourceType.PRACTITIONER)
    party_id = f"{practitioner_details.identifier[0].value},{practitioner_details.identifier[1].value}"

    patient_details = finders.find_resource(fhir_operation=fhir_operation, resource_type=ResourceType.PATIENT)
    birth_location = patient_details.extension[0].valueAddress.city

    msg_seg_registration_details = MessageSegmentBirthRegistrationDetails(transaction_number=transaction_number,
                                                                          party_id=party_id,
                                                                          acceptance_code=acceptance_code,
                                                                          acceptance_type=acceptance_type,
                                                                          date_time=fhir_operation.date.as_json(),
                                                                          location=birth_location)
    return msg_seg_registration_details
