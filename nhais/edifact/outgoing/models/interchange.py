from edifact.edifact_exception import EdifactValidationException
from edifact.outgoing.models.segment import Segment, SegmentCollection
from edifact.validation_helpers import *


class InterchangeHeader(Segment):
    """
    A specialisation of a segment for the specific use case of an interchange header
    takes in specific values required to generate an interchange header
    example: UNB+UNOA:2+TES5+XX11+920113:1317+00000002'
    """

    def __init__(self, sender, recipient, date_time, sequence_number=None):
        """
        :param sender: the sender of the interchange
        :param recipient: the intended recipient of the interchange
        :param date_time: the date time stamp of the interchange header
        :param sequence_number: a unique reference of the interchange
        """
        self.sender = sender
        self.recipient = recipient
        self.date_time = date_time
        self.sequence_number = sequence_number

    @property
    def key(self):
        return "UNB"

    @property
    def value(self):
        return f"UNOA:2+{self.sender}+{self.recipient}+{self.date_time}+{self.sequence_number}++FHSREG"

    def pre_validate(self):
        required(self, 'sender')
        required(self, 'recipient')
        required(self, 'date_time')

    def _validate_stateful(self):
        required(self, 'sequence_number')


class InterchangeTrailer(Segment):
    """
    A specialisation of a segment for the specific use case of an interchange trailer
    takes in specific values required to generate an interchange trailer
    example: UNZ+1+00000002'
    """

    def __init__(self, number_of_messages, sequence_number=None):
        """
        :param number_of_messages: the number of messages within this interchange
        :param sequence_number: a unique reference of the interchange
        """
        self.number_of_messages = number_of_messages
        self.sequence_number = sequence_number

    @property
    def key(self):
        return "UNZ"

    @property
    def value(self):
        return f"{self.number_of_messages}+{self.sequence_number}"

    def pre_validate(self):
        required(self, 'number_of_messages')

    def _validate_stateful(self):
        required(self, 'sequence_number')


class Interchange(SegmentCollection):
    """
    The edifact interchange that is used to interface with NHAIS
    It is constructed using a list of Segments
    """

    def __init__(self, sender, recipient, sequence_number, date_time, messages):
        """
        :param sender: the sender of the interchange
        :param recipient: the intended recipient of the interchange
        :param date_time: the date time stamp of the interchange header
        :param sequence_number: a unique reference of the interchange
        :param messages: The messages of the interchange
        """
        int_hdr = InterchangeHeader(sender=sender, recipient=recipient, date_time=date_time,
                                    sequence_number=sequence_number)
        int_trl = InterchangeTrailer(number_of_messages=len(messages), sequence_number=sequence_number)
        segments = [int_hdr, messages, int_trl]
        super().__init__(segments)
