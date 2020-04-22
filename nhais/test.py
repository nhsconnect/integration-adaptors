import asyncio

import sequence.dynamo_sequence
# from sequence.dynamo_sequence import DynamoSequenceGenerator
from utilities import config
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

async def main():
    db = sequence.dynamo_sequence.DynamoSequenceGenerator('transaction_id_counter')
    # await db.add('asdf', {'hello': 'world', 'sequence_number': 1})
    await db.next('global_transaction')


if __name__ == '__main__':
    config.setup_config("MHS")
    log.configure_logging("MHS")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())