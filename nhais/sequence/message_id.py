from sequence.sequence_factory import get_sequence_generator


class MessageIdGenerator:
    """A component that provides sequential message id
    Definition:
    SMS (Send Message Sequence) - sequence number applied for each message within an interchange"""

    def __init__(self):
        self.table_name = 'transaction_id_counter'

    async def generate_message_id(self, sender, recipient) -> int:
        key = "SMS-" + str(sender) + "-" + str(recipient)
        message_generator = get_sequence_generator(self.table_name)
        return await message_generator.next(key)
