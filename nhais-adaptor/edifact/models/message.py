from datetime import datetime
from edifact.models.segment import Segment, SegmentCollection


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
        formatted_date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y%m%d%H%M')
        segments = [
            Segment(key="BGM", value="++507"),
            Segment(key="NAD", value=f"FHS+{party_id}:954"),
            Segment(key="DTM", value=f"137:{formatted_date_time}:203"),
            Segment(key="RFF", value=f"950:{ref_number}"),
        ]
        super().__init__(segments=segments)


class Message(SegmentCollection):
    """
    An edifact Message that is contained within an interchange
    a collection of Segments
    """

    def __init__(self, header, message_beginning, trailer):
        """
        :param header: the header of the message
        :param message_beginning: the beginning of the message
        :param trailer: the trailer of the message
        """
        segments = [header, message_beginning, trailer]
        super().__init__(segments=segments)

