import asyncio
from datetime import datetime

from fhir.resources.patient import Patient

from edifact.outgoing.models.interchange import InterchangeHeader, InterchangeTrailer
from edifact.outgoing.models.message import MessageHeader, MessageTrailer, ReferenceTransactionNumber, \
    ReferenceTransactionType
from outbound.converter.fhir_helpers import get_ha_identifier, get_gp_identifier
from outbound.converter.stub_message_translator import StubMessageTranslator
from outbound.state.work_description import WorkDescription, create_new_work_description
from sequence.sequence_manager import IdGenerator
from utilities.date_utilities import DateUtilities
from persistence.persistence_adaptor_factory import get_persistence_adaptor


class InterchangeTranslator(object):

    def __init__(self):
        self.id_generator = IdGenerator()
        self.segments = []

    async def convert(self, patient: Patient, transaction_type: ReferenceTransactionType.TransactionType) -> str:
        translation_timestamp = DateUtilities.utc_now()
        sender, recipient = self.__append_interchange_header(patient, translation_timestamp)
        self.__append_message_segments(patient, translation_timestamp)
        self.segments.append(InterchangeTrailer(number_of_messages=1))
        self.segments.append(ReferenceTransactionType(transaction_type))

        # pre-validate to ensure the EDIFACT message is valid before generating sequence numbers for it
        self.__pre_validate_segments()
        await self.__generate_identifiers(sender, recipient)
        await self.__record_outgoing_state()
        return self.__translate_edifact()

    def __append_interchange_header(self, patient, translation_timestamp: datetime):
        sender = get_gp_identifier(patient)
        recipient = get_ha_identifier(patient)
        self.segments.append(InterchangeHeader(sender=sender, recipient=recipient, date_time=translation_timestamp))
        return sender, recipient

    def __append_message_segments(self, patient: Patient, translation_timestamp: datetime):
        message_translator = StubMessageTranslator(translation_timestamp)
        self.segments.extend(message_translator.translate(patient))

    def __pre_validate_segments(self):
        for segment in self.segments:
            segment.pre_validate()

    async def __generate_identifiers(self, sender, recipient):
        interchange_id, message_id, transaction_id = await asyncio.gather(
            self.id_generator.generate_interchange_id(sender, recipient),
            self.id_generator.generate_message_id(sender, recipient),
            self.id_generator.generate_transaction_id()
        )
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
        adaptor = get_persistence_adaptor(**{'table_name': 'nhais_state'})
        work_description = create_new_work_description(adaptor, self.segments)
        await work_description.publish()
        return
