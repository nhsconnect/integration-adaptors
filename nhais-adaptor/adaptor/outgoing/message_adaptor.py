from fhirclient.models.operationdefinition import OperationDefinition

import adaptor.fhir_helpers.fhir_finders as finders
from adaptor.fhir_helpers.fhir_creators import ParameterName
from edifact.outgoing.models.birth.message_birth import Message
from edifact.outgoing.models.message import MessageBeginning, MessageSegmentPatientDetails, \
    MessageSegmentRegistrationDetails
from abc import ABC, abstractmethod


class MessageAdaptor(ABC):

    def __init__(self, fhir_operation: OperationDefinition):
        self.fhir_operation = fhir_operation

    @abstractmethod
    def create_message_beginning(self) -> MessageBeginning:
        pass

    @abstractmethod
    def create_message_segment_patient_detail(self) -> MessageSegmentPatientDetails:
        pass

    @abstractmethod
    def create_message_segment_registration_details(self) -> MessageSegmentRegistrationDetails:
        pass

    def create_message(self) -> Message:
        """
        Create the edifact Message
        :return: Message
        """
        message_sequence_number = finders.get_parameter_value(fhir_operation=self.fhir_operation,
                                                              parameter_name=ParameterName.MESSAGE_SEQ_NO)

        message_bgn = self.create_message_beginning()
        patient_details = self.create_message_segment_patient_detail()
        registration_details = self.create_message_segment_registration_details()
        message = Message(sequence_number=message_sequence_number,
                          message_beginning=message_bgn,
                          message_segment_registration_details=registration_details,
                          message_segment_patient_details=patient_details)

        return message
