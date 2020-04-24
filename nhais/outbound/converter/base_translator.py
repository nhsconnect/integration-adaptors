from fhir.resources.identifier import Identifier
from fhir.resources.organization import Organization
from fhir.resources.practitioner import Practitioner

from edifact.outgoing.models.interchange import InterchangeHeader, InterchangeTrailer
from edifact.outgoing.models.message import Messages, MessageHeader, MessageTrailer
from outbound.converter.base_message_translator import BaseMessageTranslator
from sequence.interchange import InterchangeIdGenerator
from sequence.message import MessageIdGenerator
from sequence.transaction import TransactionIdGenerator
from fhir.resources.patient import Patient
from datetime import datetime


class BaseFhirToEdifactTranslator(object):

    def __init__(self):
        self.transaction_id_generator = TransactionIdGenerator()
        self.message_id_generator = MessageIdGenerator()
        self.interchange_id_generator = InterchangeIdGenerator()
        self.edi_segments = []

    async def convert(self, patient: Patient):
        # TODO: what if the request is an Amendment? Not a Patient but JSONPatch!
        self.__append_header_segments(patient)
        self.__append_message_segments(patient)
        self.__append_trailer_segments(patient)
        self.__pre_validate_segments()
        await self.__generate_identifiers()
        await self.__record_outgoing_state()
        return self.__translate_edifact()

    def __append_header_segments(self, body):
        self.edi_segments.append(self.__interchange_header(body))

    def __append_trailer_segments(self, body):
        self.edi_segments.append(self.__interchange_trailer())

    def __append_message_segments(self, patient: Patient):
        # TODO: pick a message translator based on the type of request
        message_translator = BaseMessageTranslator()
        self.edi_segments.extend(message_translator.translate(patient))
        pass

    def __interchange_header(self, patient) -> InterchangeHeader:
        gp = patient.generalPractitioner[0]  # type: Practitioner
        gp_identifier = gp.identifier[0]  # type: Identifier
        sender = gp_identifier.value
        ha = patient.managingOrganization[0]  # type: Organization
        ha_identifier = ha.identifier[0]  # type: Identifier
        recipient = ha_identifier.value
        return InterchangeHeader(sender=sender, recipient=recipient, date_time=datetime.utcnow())

    def __interchange_trailer(self) -> InterchangeTrailer:
        number_of_messages = 1
        return InterchangeTrailer(number_of_messages)

    def __pre_validate_segments(self):
        for segment in self.edi_segments:
            segment.pre_validate()

    async def __generate_identifiers(self):
        interchange_id = self.interchange_id_generator.next_interchange_id()
        message_id = self.message_id_generator.next_message_id()
        for segment in self.edi_segments:
            if isinstance(segment, (InterchangeHeader, InterchangeTrailer)):
                segment.sequence_number = interchange_id
            if isinstance(segment, (MessageHeader, MessageTrailer)):
                segment.sequence_number = message_id

    def __translate_edifact(self):
        return '\n'.join([segment.to_edifact() for segment in self.edi_segments])

    async def __record_outgoing_state(self):
        return
