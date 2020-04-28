from datetime import datetime

from edifact.validation_helpers import *

TIMESTAMP_FORMAT ='%y%m%d:%H%M'


class InterchangeHeader(Segment):
    """
    A specialisation of a segment for the specific use case of an interchange header
    takes in specific values required to generate an interchange header
    example: UNB+UNOA:2+TES5+XX11+920113:1317+00000002'
    """

    def __init__(self, sender, recipient, date_time: datetime, sequence_number: (None, int) = None):
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
        formatted_date_time = self.date_time.strftime(TIMESTAMP_FORMAT)
        formatted_sequence_number = f'{self.sequence_number:08}'
        # nhais-adaptor version has '++FHSREG' appended to the end which doesn't seem correct
        return f"UNOA:2+{self.sender}+{self.recipient}+{formatted_date_time}+{formatted_sequence_number}"

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

    def __init__(self, number_of_messages: int, sequence_number: (None, int) = None):
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
        formatted_sequence_number = f'{self.sequence_number:08}'
        return f"{self.number_of_messages}+{formatted_sequence_number}"

    def pre_validate(self):
        required(self, 'number_of_messages')

    def _validate_stateful(self):
        required(self, 'sequence_number')
