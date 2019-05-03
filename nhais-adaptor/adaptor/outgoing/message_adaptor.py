from edifact.outgoing.models.message import MessageSegmentPatientDetails, MessageSegmentRegistrationDetails, \
    MessageBeginning, \
    Message
from edifact.outgoing.models.name import Name
from edifact.outgoing.models.address import Address
import adaptor.fhir_helpers.fhir_finders as finders
from adaptor.fhir_helpers.fhir_creators import ParameterName, ResourceType, OperationName

operation_dict = {
    OperationName.REGISTER_BIRTH: {
        "acceptanceCode": "A",
        "acceptanceType": "1",
        "refNumber": "G1"
    }
}


def create_patient_name(fhir_patient_name):
    """
    Function to generate the edifact representation of the patient name
    :param fhir_patient_name: fhir representation of the patient name
    :return: edifact name
    """
    given_names = [None, None, None]
    for index, given_name in enumerate(fhir_patient_name.given):
        given_names[index] = given_name

    edi_name = Name(title=fhir_patient_name.prefix[0],
                    family_name=fhir_patient_name.family,
                    first_given_forename=fhir_patient_name.given[0],
                    middle_name=given_names[1],
                    third_given_forename=given_names[2])
    return edi_name


def determine_address_lines(fhir_patient_address_lines):
    """
    This function generates a uniform list of address lines always returning a list of 3 lines.
    The result of this can be used to populate the edifact address model
    Since the fhir patient address does not have anything specifically for house name in its definition.
    This function assumes that if 3 address lines are provided then the first line is the house name
    if it is less than 3 then always default the first line as "".
    :param fhir_patient_address_lines: the fhir representation for the patient address
    :return: a uniform list of address lines to populate the edifact address model
    """
    address_lines = ["", "", ""]
    counter = 0 if len(fhir_patient_address_lines) == 3 else 1

    for line in fhir_patient_address_lines:
        address_lines[counter] = line
        counter += 1

    return address_lines


def create_patient_address(fhir_patient_address):
    """
    Function to generate the edifact representation of the patient address
    :param fhir_patient_address: The fhir representation of the patient address
    :return: edifact address
    """
    address_lines = determine_address_lines(fhir_patient_address.line)

    edi_address = Address(house_name=address_lines[0],
                          address_line_1=address_lines[1],
                          address_line_2=address_lines[2],
                          town=fhir_patient_address.city,
                          county=fhir_patient_address.district if fhir_patient_address.district else "",
                          post_code=fhir_patient_address.postalCode)
    return edi_address


def create_message_segment_patient_detail(fhir_operation):
    """
    :return: MessageSegmentPatientDetails
    """
    gender_map = {'unknown': 0, 'male': 1, 'female': 2, 'other': 9}

    patient = finders.find_resource(fhir_operation, resource_type=ResourceType.PATIENT)

    edi_name = create_patient_name(patient.name[0])

    edi_address = create_patient_address(patient.address[0])

    msg_seg_patient_details = MessageSegmentPatientDetails(id_number=patient.identifier[0].value,
                                                           name=edi_name,
                                                           date_of_birth=patient.birthDate.as_json(),
                                                           gender=gender_map[patient.gender],
                                                           address=edi_address)
    return msg_seg_patient_details


def create_message_segment_registration_details(fhir_operation):
    """
    Create the message segment registration details from the fhir operation
    :return: MessageSegmentRegistrationDetails
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

    msg_seg_registration_details = MessageSegmentRegistrationDetails(transaction_number=transaction_number,
                                                                     party_id=party_id,
                                                                     acceptance_code=acceptance_code,
                                                                     acceptance_type=acceptance_type,
                                                                     date_time=fhir_operation.date.as_json(),
                                                                     location=birth_location)
    return msg_seg_registration_details


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
    message = Message(sequence_number=message_sequence_number,
                      message_beginning=create_message_beginning(fhir_operation),
                      message_segment_registration_details=create_message_segment_registration_details(
                          fhir_operation),
                      message_segment_patient_details=create_message_segment_patient_detail(
                          fhir_operation))

    return message
