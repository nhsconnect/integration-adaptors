from edifact.outgoing.models.interchange import InterchangeHeader, InterchangeTrailer
from edifact.outgoing.models.message import Messages
from sequence.interchange import InterchangeIdGenerator
from sequence.message import MessageIdGenerator
from sequence.transaction import TransactionIdGenerator


class BaseFhirToEdifactTranslator(object):

    def __init__(self):
        self.transaction_id_generator = TransactionIdGenerator()
        self.message_id_generator = MessageIdGenerator()
        self.interchange_id_generator = InterchangeIdGenerator()
        self.edi_segments = []

    async def convert(self, body):
        self.__append_header_segments(body)
        self.__append_message_segments(body)
        self.__append_trailer_segments(body)
        self.__pre_validate_segments()
        await self.__generate_identifiers()
        await self.__record_outgoing_state()
        return self.__translate_edifact()

    def __append_header_segments(self, body):
        self.edi_segments.append(self.__interchange_header(body))

    def __append_trailer_segments(self, body):
        self.edi_segments.append(self.__interchange_trailer())

    def __append_message_segments(self, body):
        pass

    def __interchange_header(self, patient) -> InterchangeHeader:
        sender = 'SENDER'
        recipient = 'RECIPIENT'
        date_time = 'now'
        return InterchangeHeader(sender=sender, recipient=recipient, date_time=date_time)

    def __interchange_trailer(self) -> InterchangeTrailer:
        number_of_messages = 1
        return InterchangeTrailer(number_of_messages)

    def __pre_validate_segments(self):
        for segment in self.edi_segments:
            segment.pre_validate()

    async def __generate_identifiers(self):
        interchange_id = self.interchange_id_generator.next_interchange_id()

        for segment in self.edi_segments:
            if isinstance(segment, (InterchangeHeader, InterchangeTrailer)):
                segment.sequence_number = interchange_id

    def __translate_edifact(self):
        return '\n'.join([segment.to_edifact() for segment in self.edi_segments])

    async def __record_outgoing_state(self):
        return
