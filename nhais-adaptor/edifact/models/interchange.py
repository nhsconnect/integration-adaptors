from datetime import datetime
from edifact.models.segment import Segment


class InterchangeHeader(Segment):
    """
    A specialisation of a segment for the specific use case of an interchange header
    takes in specific values required to generate an interchange header
    example: UNB+UNOA:2+TES5+XX11+920113:1317+00000002'
    """

    SEGMENT_KEY = "UNB"

    def __init__(self, sender, recipient, date_time, sequence_number):
        """
        :param sender: the sender of the interchange
        :param recipient: the intended recipient of the interchange
        :param date_time: the date time stamp of the interchange header
        :param sequence_number: a unique reference of the interchange
        """
        formatted_date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f').strftime('%y%m%d:%H%M')
        segment_value = f"UNOA:2+{sender}+{recipient}+{formatted_date_time}+{sequence_number}"
        super().__init__(key=self.SEGMENT_KEY, value=segment_value)


class InterchangeTrailer(Segment):
    """
    A specialisation of a segment for the specific use case of an interchange trailer
    takes in specific values required to generate an interchange trailer
    example: UNZ+1+00000002'
    """

    SEGMENT_KEY = "UNZ"

    def __init__(self, number_of_messages, sequence_number):
        """
        :param number_of_messages: the number of messages within this interchange
        :param sequence_number: a unique reference of the interchange
        """
        segment_value = f"{number_of_messages}+{sequence_number}"
        super().__init__(key=self.SEGMENT_KEY, value=segment_value)


class Interchange(object):
    """
    The edifact interchange that is used to interface with NHAIS
    """

    def __init__(self, header):
        """
        :param header: The header of the interchange
        """
        self.header = header

    def to_edifact(self):
        edifact_interchange = f"AAA-{self.header}"
        return edifact_interchange
