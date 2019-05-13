import adaptor.fhir_helpers.fhir_finders as finders
from adaptor.fhir_helpers.fhir_creators import ResourceType, ParameterName
from adaptor.outgoing.message_adaptor import MessageAdaptor
from edifact.outgoing.models.death.message_death import MessageSegmentDeathPatientDetails, \
    MessageSegmentDeathRegistrationDetails
import adaptor.outgoing.common.date_formatter as date_formatter


class MessageDeathAdaptor(MessageAdaptor):

    def get_reference_number(self) -> str:
        """
        Returns the unique reference number to indicate a death registration in the edifact payload
        :return: a string representing a death registration
        """
        return "G5"

    def create_message_segment_patient_detail(self) -> MessageSegmentDeathPatientDetails:
        """
        Create the message segment patient details for a death from the fhir operation
        :return: MessageSegmentDeathPatientDetails
        """
        patient = finders.find_resource(self.fhir_operation, resource_type=ResourceType.PATIENT)

        msg_seg_patient_details = MessageSegmentDeathPatientDetails(id_number=patient.identifier[0].value)
        return msg_seg_patient_details

    def create_message_segment_registration_details(self) -> MessageSegmentDeathRegistrationDetails:
        """
        Create the message segment registration details for a death from the fhir operation
        :return: MessageSegmentDeathRegistrationDetails
        """

        transaction_number = finders.get_parameter_value(fhir_operation=self.fhir_operation,
                                                         parameter_name=ParameterName.TRANSACTION_NO)

        practitioner_details = finders.find_resource(fhir_operation=self.fhir_operation,
                                                     resource_type=ResourceType.PRACTITIONER)
        party_id = f"{practitioner_details.identifier[0].value},{practitioner_details.identifier[1].value}"

        patient_details = finders.find_resource(fhir_operation=self.fhir_operation, resource_type=ResourceType.PATIENT)

        deceased_date_time = patient_details.deceasedDateTime.as_json()
        formatted_deceased_date_time = date_formatter.format_date(date_time=deceased_date_time, format_qualifier="102")

        free_text = finders.get_parameter_value(fhir_operation=self.fhir_operation,
                                                parameter_name=ParameterName.FREE_TEXT)

        msg_seg_registration_details = MessageSegmentDeathRegistrationDetails(transaction_number=transaction_number,
                                                                              party_id=party_id,
                                                                              date_time=formatted_deceased_date_time,
                                                                              free_text=free_text)
        return msg_seg_registration_details
