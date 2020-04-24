import abc

from fhir.resources.patient import Patient

from edifact.outgoing.models.message import MessageHeader, MessageTrailer


class BaseMessageTranslator:

    def __init__(self):
        self.segments = []

    def translate(self, patient: Patient):
        self.segments.append(MessageHeader())
        self._translate_body(patient)
        number_of_segments = len(self.segments) + 1
        self.segments.append(MessageTrailer(number_of_segments=number_of_segments))
        return self.segments

    @abc.abstractmethod
    def _translate_body(self, patient: Patient):
        pass
