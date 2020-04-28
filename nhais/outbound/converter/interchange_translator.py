from datetime import datetime

from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner

from edifact.outgoing.models.interchange import InterchangeHeader, InterchangeTrailer
from edifact.outgoing.models.message import MessageHeader, MessageTrailer, ReferenceTransactionNumber
from outbound.converter.base_message_translator import BaseMessageTranslator
from outbound.converter.fhir_helpers import get_ha_identifier
from sequence.interchange import InterchangeIdGenerator
from sequence.message import MessageIdGenerator
from sequence.transaction import TransactionIdGenerator
from utilities.date_utilities import DateUtilities


class InterchangeTranslator(object):

    def __init__(self):
        self.transaction_id_generator = TransactionIdGenerator()
        self.message_id_generator = MessageIdGenerator()
        self.interchange_id_generator = InterchangeIdGenerator()
        self.segments = []

    async def convert(self, patient: Patient):
        # TODO: NIAD-108 what if the request is an Amendment? Payload is not a Patient but JSONPatch!
        translation_timestamp = DateUtilities.utcnow()
        self.__append_interchange_header(patient, translation_timestamp)
        self.__append_message_segments(patient, translation_timestamp)
        self.segments.append(InterchangeTrailer(number_of_messages=1))

        self.__pre_validate_segments()
        await self.__generate_identifiers()
        await self.__record_outgoing_state()
        return self.__translate_edifact()

    def __append_interchange_header(self, patient, translation_timestamp: datetime):
        gp = patient.generalPractitioner[0]  # type: Practitioner
        sender = gp.identifier.value
        recipient = get_ha_identifier(patient)
        self.segments.append(InterchangeHeader(sender=sender, recipient=recipient, date_time=translation_timestamp))

    def __append_message_segments(self, patient: Patient, translation_timestamp: datetime):
        # TODO: pick a message translator based on the type of request
        message_translator = BaseMessageTranslator(translation_timestamp)
        self.segments.extend(message_translator.translate(patient))

    def __pre_validate_segments(self):
        for segment in self.segments:
            segment.pre_validate()

    async def __generate_identifiers(self):
        interchange_id = self.interchange_id_generator.next_interchange_id()
        message_id = self.message_id_generator.next_message_id()
        transaction_id = self.transaction_id_generator.next_transaction_id()
        for segment in self.segments:
            if isinstance(segment, (InterchangeHeader, InterchangeTrailer)):
                segment.sequence_number = interchange_id
            if isinstance(segment, (MessageHeader, MessageTrailer)):
                segment.sequence_number = message_id
            if isinstance(segment, ReferenceTransactionNumber):
                segment.reference = transaction_id


    def __translate_edifact(self):
        return '\n'.join([segment.to_edifact() for segment in self.segments])

    async def __record_outgoing_state(self):
        return
