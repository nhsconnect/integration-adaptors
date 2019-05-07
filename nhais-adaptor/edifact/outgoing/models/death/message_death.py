from edifact.helpers import date_formatter as date_formatter
from edifact.outgoing.models.message import MessageSegmentRegistrationDetails, MessageSegmentPatientDetails, Message
from edifact.outgoing.models.segment import Segment


class MessageSegmentDeathPatientDetails(MessageSegmentPatientDetails):
    """
    A specialisation of the MessageSegmentPatientDetails class for the purpose of a Death
    """

    def __init__(self, id_number):
        """
        :param id_number: OPI official Payment Id (existing NHS Number)
        """
        segments = [
            Segment(key="PNA", value=f"PAT+{id_number}:OPI"),
        ]
        super().__init__()
        super().add_segments(segments)


class MessageSegmentDeathRegistrationDetails(MessageSegmentRegistrationDetails):
    """
    A specialisation of the MessageSegmentRegistrationDetails class for the purpose of a Death
    """

    def __init__(self, transaction_number, party_id, date_time, free_text=None):
        """
        :param transaction_number: a unique transaction number. NHAIS will reference this in its response
        :param party_id: GMC National code and the Local GP Code of the patient's GP (separated by “,”).
        :param date_time: date of the patient deduction
        :param free_text: optional free text
        """
        formatted_date_time = date_formatter.format_date(date_time=date_time, format_qualifier="102")
        segments = [
            Segment(key="GIS", value=f"1:ZZZ"),
            Segment(key="DTM", value=f"961:{formatted_date_time}:102"),
        ]
        if free_text:
            segments.append(
                Segment(key="FTX", value=f"RGI+++{free_text}")
            )
        super().__init__(transaction_number=transaction_number, party_id=party_id)
        super().add_segments(segments)


class MessageTypeDeath(Message):
    """
    A specialisation of the Message for the purpose of a Death registration
    """
    def __init__(self, sequence_number, message_beginning,
                 message_segment_registration_details: MessageSegmentDeathRegistrationDetails,
                 message_segment_patient_details: MessageSegmentDeathPatientDetails):
        """
        :param sequence_number: the unique sequence number of the message
        :param message_beginning: the beginning of the message
        :param message_segment_registration_details: Segment trigger 1 registration information
        :param message_segment_patient_details: Segment trigger 2 personal information about patient
        """
        super().__init__(sequence_number, message_beginning, message_segment_registration_details,
                         message_segment_patient_details)
