from sequence.dynamo_sequence import DynamoSequenceGenerator


class TransactionIdGenerator:
    """A component that provides sequential transaction id"""

    def __init__(self):
        self.table_name = 'transaction_id_counter'
        self.key = 'transaction_id'

    async def generate_transaction_id(self) -> int:
        transaction_generator = DynamoSequenceGenerator(self.table_name)
        return await transaction_generator.next(self.key)
