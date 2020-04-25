from sequence.dynamo_sequence import DynamoSequenceGenerator


class TransactionIdGenerator:
    """A component that provides sequential transaction id"""

    async def generate_transaction_id(self) -> int:
        table = 'transaction_id_counter'
        key = 'transaction_id'

        transaction_generator = DynamoSequenceGenerator(table)
        return await transaction_generator.next(key)
