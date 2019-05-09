import adaptor.fhir_helpers.fhir_finders as finders
from adaptor.fhir_helpers.fhir_creators import ResourceType, ParameterName
from adaptor.outgoing.message_adaptor import MessageAdaptor
from edifact.outgoing.models.death.message_death import MessageSegmentDeathPatientDetails, \
    MessageSegmentDeathRegistrationDetails
from edifact.outgoing.models.message import MessageBeginning


class MessageDeathAdaptor(MessageAdaptor):

    def create_message_beginning(self) -> MessageBeginning:
        """
        Create the beginning of the message
        :return: MessageBeginning
        """
        nhais_id = finders.get_parameter_value(fhir_operation=self.fhir_operation,
                                               parameter_name=ParameterName.NHAIS_CYPHER)

        ref_number = "G5"

        msg_bgn = MessageBeginning(party_id=nhais_id, date_time=self.fhir_operation.date.as_json(),
                                   ref_number=ref_number)

        return msg_bgn

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

        free_text = finders.get_parameter_value(fhir_operation=self.fhir_operation,
                                                parameter_name=ParameterName.FREE_TEXT)

        msg_seg_registration_details = MessageSegmentDeathRegistrationDetails(transaction_number=transaction_number,
                                                                              party_id=party_id,
                                                                              date_time=deceased_date_time,
                                                                              free_text=free_text)
        return msg_seg_registration_details
