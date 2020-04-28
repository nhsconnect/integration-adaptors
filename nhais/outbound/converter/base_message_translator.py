import abc
from datetime import datetime

from fhir.resources.patient import Patient

from edifact.outgoing.models.message import MessageHeader, MessageTrailer, BeginningOfMessage, NameAndAddress, \
    DateTimePeriod, SegmentGroup, ReferenceTransactionNumber
from outbound.converter.fhir_helpers import get_ha_identifier


class BaseMessageTranslator(abc.ABC):

    def __init__(self, translation_timestamp: datetime):
        self.segments = []
        self.translation_timestamp = translation_timestamp

    def translate(self, patient: Patient):
        self.segments.append(MessageHeader())
        self.segments.append(BeginningOfMessage())
        self.segments.append(NameAndAddress(NameAndAddress.QualifierAndCode.FHS, get_ha_identifier(patient)))
        self.segments.append(DateTimePeriod(DateTimePeriod.TypeAndFormat.TRANSLATION_TIMESTAMP, self.translation_timestamp))
        self._append_transaction_type()
        self.segments.append(SegmentGroup(1))
        self.segments.append(ReferenceTransactionNumber())
        self._append_message_body(patient)
        number_of_segments = len(self.segments) + 1
        self.segments.append(MessageTrailer(number_of_segments=number_of_segments))
        return self.segments

    @abc.abstractmethod
    def _append_transaction_type(self):
        """
        Appends an RFF+950 segment (ReferenceTransactionType) for the type of message represented by this class
        """
        pass

    @abc.abstractmethod
    def _append_message_body(self, patient: Patient):
        """
        Appends the remainder of Segment Group 1 and all of Segment Group 2
        :param patient: the FHIR Patient
        """
        pass
