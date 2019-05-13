import adaptor.fhir_helpers.fhir_finders as finders
import adaptor.outgoing.common.date_formatter as date_formatter
from adaptor.fhir_helpers.fhir_creators import ResourceType, ParameterName
from adaptor.outgoing.common.common_adaptor import create_patient_name, create_patient_address
from adaptor.outgoing.message_adaptor import MessageAdaptor
from edifact.outgoing.models.birth.message_birth import MessageSegmentBirthPatientDetails, \
    MessageSegmentBirthRegistrationDetails


class MessageBirthAdaptor(MessageAdaptor):

    def get_reference_number(self) -> str:
        """
        Returns the unique reference number to indicate a birth registration in the edifact payload
        :return: a string representing a birth registration
        """
        return "G1"

    def create_message_segment_patient_detail(self) -> MessageSegmentBirthPatientDetails:
        """
        Create the message segment patient details for a birth registration from the fhir operation
        :return: MessageSegmentBirthPatientDetails
        """
        gender_map = {'unknown': 0, 'male': 1, 'female': 2, 'other': 9}

        patient = finders.find_resource(self.fhir_operation, resource_type=ResourceType.PATIENT)

        edi_name = create_patient_name(patient.name[0])

        edi_address = create_patient_address(patient.address[0])

        formatted_date_of_birth = date_formatter.format_date(date_time=patient.birthDate.as_json(),
                                                             format_qualifier="102", current_format="%Y-%m-%d")

        msg_seg_patient_details = MessageSegmentBirthPatientDetails(id_number=patient.identifier[0].value,
                                                                    name=edi_name,
                                                                    date_of_birth=formatted_date_of_birth,
                                                                    gender=gender_map[patient.gender],
                                                                    address=edi_address)
        return msg_seg_patient_details

    def create_message_segment_registration_details(self) -> MessageSegmentBirthRegistrationDetails:
        """
        Create the message segment registration details for a birth registration from the fhir operation
        :return: MessageSegmentBirthRegistrationDetails
        """

        transaction_number = finders.get_parameter_value(fhir_operation=self.fhir_operation,
                                                         parameter_name=ParameterName.TRANSACTION_NO)

        practitioner_details = finders.find_resource(fhir_operation=self.fhir_operation,
                                                     resource_type=ResourceType.PRACTITIONER)
        party_id = f"{practitioner_details.identifier[0].value},{practitioner_details.identifier[1].value}"

        patient_details = finders.find_resource(fhir_operation=self.fhir_operation, resource_type=ResourceType.PATIENT)
        birth_location = patient_details.extension[0].valueAddress.city
        formatted_date_time = date_formatter.format_date(date_time=self.fhir_operation.date.as_json(),
                                                         format_qualifier="102")

        msg_seg_registration_details = MessageSegmentBirthRegistrationDetails(transaction_number=transaction_number,
                                                                              party_id=party_id,
                                                                              date_time=formatted_date_time,
                                                                              location=birth_location)
        return msg_seg_registration_details
