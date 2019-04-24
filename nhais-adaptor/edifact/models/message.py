from edifact.models.segment import Segment


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


class Message(object):
    """
    An edifact Message that is contained within an interchange
    a collection of Segments
    """

    def __init__(self, header, trailer):
        """
        :param header: the header of the message
        :param trailer: the trailer of the message
        """
        self.segments = [header, trailer]

    def to_edifact(self):
        edifact_message = ''.join([segment.to_edifact() for segment in self.segments])
        return edifact_message

