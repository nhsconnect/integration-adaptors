from sequence.sequence_factory import get_sequence_generator


class InterchangeIdGenerator:
    """A component that provides sequential interchange id.
    Definition:
    SIS (Send Interchange Sequence) - sequence number for the entire EDIFACT interchange """

    def __init__(self):
        self.table_name = 'generated_id_counter'

    async def generate_interchange_id(self, sender, recipient) -> int:
        key = f"SIS-{sender}-{recipient}"
        interchange_generator = get_sequence_generator(self.table_name)
        return await interchange_generator.next(key)
