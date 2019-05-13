from adaptor.outgoing.common import date_formatter as date_formatter
from edifact.outgoing.models.address import PatientAddress
from edifact.outgoing.models.message import MessageSegmentRegistrationDetails, MessageSegmentPatientDetails, Message
from edifact.outgoing.models.name import PatientName
from edifact.outgoing.models.segment import Segment


class MessageSegmentBirthPatientDetails(MessageSegmentPatientDetails):
    """
    A specialisation of the MessageSegmentPatientDetails class for the purpose of a Birth
    """

    def __init__(self, id_number, name, date_of_birth, gender, address):
        """
        :param id_number: OPI official Patient Id (existing NHS Number)
        :param name: the name of the patient
        :param date_of_birth: Patients date of birth
        :param gender: sex of the patient. For an acceptance transaction, reference "G1", this segment is required
        :param address: the patients address
        """
        formatted_date = date_formatter.format_date(date_time=date_of_birth, format_qualifier="102",
                                                    current_format="%Y-%m-%d")
        segments = [
            PatientName(id_number=id_number, name=name),
            Segment(key="DTM", value=f"329:{formatted_date}:102"),
            Segment(key="PDI", value=f"{gender}"),
            PatientAddress(address=address)
        ]
        super().__init__()
        super().add_segments(segments)


class MessageSegmentBirthRegistrationDetails(MessageSegmentRegistrationDetails):
    """
    A specialisation of the MessageSegmentRegistrationDetails class for the purpose of a Birth
    """

    def __init__(self, transaction_number, party_id, date_time, location):
        """
        :param transaction_number: a unique transaction number. NHAIS will reference this in its response
        :param party_id: GMC National code and the Local GP Code of the patient's GP (separated by “,”).
        :param date_time: date of the registration
        :param location: the patients place of birth
        """
        formatted_date_time = date_formatter.format_date(date_time=date_time, format_qualifier="102")
        segments = [
            Segment(key="HEA", value=f"ACD+A:ZZZ"),
            Segment(key="HEA", value=f"ATP+1:ZZZ"),
            Segment(key="DTM", value=f"956:{formatted_date_time}:102"),
            Segment(key="LOC", value=f"950+{location}"),
        ]
        super().__init__(transaction_number=transaction_number, party_id=party_id)
        super().add_segments(segments)


class BirthRegistrationMessage(Message):
    """
    A specialisation of the Message for the purpose of a Birth registration
    """

    def __init__(self, sequence_number, message_beginning,
                 message_segment_registration_details: MessageSegmentBirthRegistrationDetails,
                 message_segment_patient_details: MessageSegmentBirthPatientDetails):
        """
        :param sequence_number: the unique sequence number of the message
        :param message_beginning: the beginning of the message
        :param message_segment_registration_details: Segment trigger 1 registration information
        :param message_segment_patient_details: Segment trigger 2 personal information about patient
        """
        super().__init__(sequence_number, message_beginning, message_segment_registration_details,
                         message_segment_patient_details)
