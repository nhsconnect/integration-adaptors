import adaptor.fhir_helpers.fhir_finders as finders
from adaptor.fhir_helpers.fhir_creators import ResourceType, ParameterName, OperationName
from edifact.outgoing.models.death.message_death import MessageSegmentDeathPatientDetails, \
    MessageSegmentDeathRegistrationDetails


def create_message_segment_patient_detail(fhir_operation):
    """
    :return: MessageSegmentDeathPatientDetails
    """
    patient = finders.find_resource(fhir_operation, resource_type=ResourceType.PATIENT)

    msg_seg_patient_details = MessageSegmentDeathPatientDetails(id_number=patient.identifier[0].value)
    return msg_seg_patient_details


def create_message_segment_registration_details(fhir_operation):
    """
    Create the message segment registration details from the fhir operation
    :return: MessageSegmentDeathRegistrationDetails
    """

    transaction_number = finders.get_parameter_value(fhir_operation=fhir_operation,
                                                     parameter_name=ParameterName.TRANSACTION_NO)

    practitioner_details = finders.find_resource(fhir_operation=fhir_operation,
                                                 resource_type=ResourceType.PRACTITIONER)
    party_id = f"{practitioner_details.identifier[0].value},{practitioner_details.identifier[1].value}"

    patient_details = finders.find_resource(fhir_operation=fhir_operation, resource_type=ResourceType.PATIENT)

    deceased_date_time = patient_details.deceasedDateTime.as_json()

    msg_seg_registration_details = MessageSegmentDeathRegistrationDetails(transaction_number=transaction_number,
                                                                          party_id=party_id,
                                                                          date_time=deceased_date_time)
    return msg_seg_registration_details

