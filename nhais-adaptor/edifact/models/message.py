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

