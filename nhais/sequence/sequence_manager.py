from sequence.sequence_factory import get_sequence_generator


class IdGenerator:
    """A component that provides sequential ids"""

    async def generate_transaction_id(self) -> int:
        """A function that provides sequential transaction id."""
        key = 'transaction_id'
        transaction_generator = get_sequence_generator(self.table_name)
        return await transaction_generator.next(key)

    async def generate_interchange_id(self, sender, recipient) -> int:
        """A function that provides sequential interchange id.
        Definition:
        SIS (Send Interchange Sequence) - sequence number for the entire EDIFACT interchange """
        key = f"SIS-{sender}-{recipient}"
        interchange_generator = get_sequence_generator(self.table_name)
        return await interchange_generator.next(key)

    async def generate_message_id(self, sender, recipient) -> int:
        """A function that provides sequential message id
        Definition:
        SMS (Send Message Sequence) - sequence number applied for each message within an interchange"""
        key = f"SMS-{sender}-{recipient}"
        message_generator = get_sequence_generator(self.table_name)
        return await message_generator.next(key)
