import edifact.helpers.date_formatter as date_formatter
from edifact.outgoing.models.segment import Segment, SegmentCollection


class MessageHeader(Segment):
    """
    A specialisation of a segment for the specific use case of a message header
    takes in specific values required to generate an message header
    example: UNH+00000003+FHSREG:0:1:FH:FHS001'
    """

    SEGMENT_KEY = "UNH"

    def __init__(self, sequence_number):
        """
        :param sequence_number: a unique reference of the message
        """
        segment_value = f"{sequence_number}+FHSREG:0:1:FH:FHS001"
        super().__init__(key=self.SEGMENT_KEY, value=segment_value)


class MessageTrailer(Segment):
    """
    A specialisation of a segment for the specific use case of a message trailer
    takes in specific values required to generate a message trailer
    example: UNT+18+00000003'
    """

    SEGMENT_KEY = "UNT"

    def __init__(self, number_of_segments, sequence_number):
        """
        :param number_of_segments: the total number of segments in the message including the header and trailer
        :param sequence_number: a unique reference of the message
        """
        segment_value = f"{number_of_segments}+{sequence_number}"
        super().__init__(key=self.SEGMENT_KEY, value=segment_value)


class MessageBeginning(SegmentCollection):
    """
    A collection of segments that represent the start of a message
    Provides details regarding the purpose of the message
    """

    def __init__(self, party_id, date_time, ref_number):
        """
        Create the collection of segments represent the beginning of a message
        :param party_id: Cipher of the NHAIS system, can be 2 or 3 characters
        :param date_time: the date time stamp of the message
        :param ref_number: a reference number for registration transaction type
        """
        formatted_date_time = date_formatter.format_date(date_time=date_time, format_qualifier="203")
        segments = [
            Segment(key="BGM", value="++507"),
            Segment(key="NAD", value=f"FHS+{party_id}:954"),
            Segment(key="DTM", value=f"137:{formatted_date_time}:203"),
            Segment(key="RFF", value=f"950:{ref_number}"),
        ]
        super().__init__(segments=segments)


class MessageSegmentRegistrationDetails(SegmentCollection):
    """
    A collection of segments to provide registration information for GP patients.
    This is referred to in edifact as segment trigger 1
    """

    def __init__(self, transaction_number, party_id):
        """
        :param transaction_number: a unique transaction number. NHAIS will reference this in its response
        :param party_id: GMC National code and the Local GP Code of the patient's GP (separated by “,”).
        """
        segments = [
            Segment(key="S01", value="1"),
            Segment(key="RFF", value=f"TN:{transaction_number}"),
            Segment(key="NAD", value=f"GP+{party_id}:900"),
        ]
        super().__init__(segments=segments)


class MessageSegmentPatientDetails(SegmentCollection):
    """
    A collection of segments that represent personal information about a patient.
    """

    def __init__(self):
        segments = [
            Segment(key="S02", value="2"),
        ]
        super().__init__(segments=segments)


class Message(SegmentCollection):
    """
    An edifact Message that is contained within an interchange
    a collection of Segments
    """

    def __init__(self, sequence_number, message_beginning,
                 message_segment_registration_details: MessageSegmentRegistrationDetails,
                 message_segment_patient_details: MessageSegmentPatientDetails):
        """
        :param sequence_number: the unique sequence number of the message
        :param message_beginning: the beginning of the message
        :param message_segment_registration_details: Segment trigger 1 registration information
        :param message_segment_patient_details: Segment trigger 2 personal information about patient
        """
        msg_header = MessageHeader(sequence_number=sequence_number)
        number_of_segments = len(message_beginning) + len(message_segment_registration_details.segments) + \
                             len(message_segment_patient_details.segments) + 2
        msg_trailer = MessageTrailer(number_of_segments=number_of_segments, sequence_number=sequence_number)
        segments = [msg_header, message_beginning, message_segment_registration_details,
                    message_segment_patient_details, msg_trailer]
        super().__init__(segments=segments)


class Messages(list):
    """
    A collection of edifact messages
    """

    def __init__(self, messages):
        """
        :param messages: a collections of messages
        """
        self.messages = messages
        super().__init__(messages)

    def to_edifact(self):
        """
        Generate the edifact messages
        :return: A string representation of all the edifact messages
        """
        edifact_message = ''.join([message.to_edifact() for message in self.messages])
        return edifact_message
