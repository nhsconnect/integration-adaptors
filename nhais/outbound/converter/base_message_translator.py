import abc

from fhir.resources.patient import Patient

from edifact.outgoing.models.message import MessageHeader, MessageTrailer, BeginningOfMessage, NameAndAddress
from edifact.outgoing.models.segment import ConstantSegment
from outbound.converter.fhir_helpers import get_ha_identifier


class BaseMessageTranslator:

    def __init__(self):
        self.segments = []

    def translate(self, patient: Patient):
        self.segments.append(MessageHeader())
        self.segments.append(BeginningOfMessage())
        self.__append_message_header_nad(patient)
        self._translate_body(patient)
        number_of_segments = len(self.segments) + 1
        self.segments.append(MessageTrailer(number_of_segments=number_of_segments))
        return self.segments

    def __append_message_header_nad(self, patient: Patient):
        recipient = get_ha_identifier(patient)
        self.segments.append(NameAndAddress(NameAndAddress.PartyQualifierAndCode.FHS, recipient))

    @abc.abstractmethod
    def _translate_body(self, patient: Patient):
        pass
