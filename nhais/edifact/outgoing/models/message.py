import enum
from datetime import datetime

from edifact.edifact_exception import EdifactValidationException
from edifact.outgoing.models.segment import Segment


class MessageHeader(Segment):
    """
    A specialisation of a segment for the specific use case of a message header
    takes in specific values required to generate an message header
    example: UNH+00000003+FHSREG:0:1:FH:FHS001'
    """

    def __init__(self, sequence_number: (int, None) = None):
        """
        :param sequence_number: a unique reference of the message
        """
        self.sequence_number = sequence_number

    @property
    def key(self):
        return "UNH"

    def _validate_stateful(self):
        self._required('sequence_number')

    @property
    def value(self):
        formatted_sequence_number = f'{self.sequence_number:08}'
        return f"{formatted_sequence_number}+FHSREG:0:1:FH:FHS001"

    def pre_validate(self):
        pass


class MessageTrailer(Segment):
    """
    A specialisation of a segment for the specific use case of a message trailer
    takes in specific values required to generate a message trailer
    example: UNT+18+00000003'
    """

    def __init__(self, number_of_segments: (None, int) = None, sequence_number: (None, int) = None):
        """
        :param number_of_segments: the total number of segments in the message including the header and trailer
        :param sequence_number: a unique reference of the message
        """
        self.number_of_segments = number_of_segments
        self.sequence_number = sequence_number

    @property
    def key(self):
        return "UNT"

    @property
    def value(self):
        formatted_sequence_number = f'{self.sequence_number:08}'
        return f"{self.number_of_segments}+{formatted_sequence_number}"

    def pre_validate(self):
        pass

    def _validate_stateful(self):
        self._required('number_of_segments')
        self._required('sequence_number')


class BeginningOfMessage(Segment):
    """
    This segment is used to provide a code for the message which indicates its use. It is a constant of EDIFACT
    example: BGM+++507'
    """

    @property
    def key(self):
        return 'BGM'

    @property
    def value(self):
        return '++507'

    def pre_validate(self):
        pass


class NameAndAddress(Segment):

    class QualifierAndCode(enum.Enum):
        FHS = ('FHS', '954')

    def __init__(self, party_qualifier_and_code: QualifierAndCode, party_identifier: str):
        (self.qualifier, self.code) = party_qualifier_and_code.value
        self.identifier = party_identifier

    @property
    def key(self):
        return 'NAD'

    @property
    def value(self):
        return f'{self.qualifier}+{self.identifier}:{self.code}'

    def pre_validate(self):
        self._required('qualifier')
        self._required('identifier')
        self._required('code')


class DateTimePeriod(Segment):

    class TypeAndFormat (enum.Enum):
        TRANSLATION_TIMESTAMP = ('137', '203', '%Y%m%d%H%M')
        PERIOD_END_DATE = ('206', '102', '%Y%m%d')

    def __init__(self, qualifier_and_code: TypeAndFormat, timestamp: datetime):
        (self.type_code, self.format_code, self.date_time_format) = qualifier_and_code.value
        self.timestamp = timestamp

    @property
    def key(self):
        return 'DTM'

    @property
    def value(self):
        formatted_date_time = self.timestamp.strftime(self.date_time_format)
        return f'{self.type_code}:{formatted_date_time}:{self.format_code}'

    def pre_validate(self):
        self._required('type_code')
        self._required('format_code')
        self._required('date_time_format')
        self._required('timestamp')


class Reference(Segment):

    def __init__(self, qualifier: str, reference: str):
        self.qualifier = qualifier
        self.reference = reference

    @property
    def key(self):
        return 'RFF'

    @property
    def value(self):
        return f'{self.qualifier}:{self.reference}'

    def pre_validate(self):
        self._required('qualifier')
        self._required('reference')


class ReferenceTransactionType(Reference):

    class TransactionType(enum.Enum):
        ACCEPTANCE = 'G1'
        AMENDMENT = 'G2'
        REMOVAL = 'G3'
        DEDUCTION = 'G5'

    def __init__(self, transaction_type: TransactionType):
        super().__init__(qualifier='950', reference=transaction_type.value)


class ReferenceTransactionNumber(Reference):

    def __init__(self, reference=''):
        super().__init__(qualifier='TN', reference=reference)

    def pre_validate(self):
        self._required('qualifier')

    def _validate_stateful(self):
        self._required('reference')


class SegmentGroup(Segment):

    def __init__(self, segment_group_number: int):
        self.segment_group_number = segment_group_number

    @property
    def key(self):
        return f'S{self.segment_group_number:02}'

    @property
    def value(self):
        return f'{self.segment_group_number}'

    def pre_validate(self):
        if not self.segment_group_number:
            raise EdifactValidationException(f'S: Attribute segment_group_number is required')
        if not isinstance(self.segment_group_number, int):
            raise EdifactValidationException(f'S: Attribute segment_group_number must be an integer')
        if self.segment_group_number not in (1, 2):
            raise EdifactValidationException(f'S: Attribute segment_group_number must be 1 or 2')
