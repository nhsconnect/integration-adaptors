import utilities.integration_adaptors_logger as log
from utilities import timing

from persistence import persistence_adaptor as pa

DATA = 'DATA'
OPERATION_ID = 'OPERATION_ID'
TRANSACTION_ID = 'TRANSACTION_ID'
TRANSACTION_TIMESTAMP = 'TRANSACTION_TIMESTAMP'
TRANSACTION_TYPE = 'TRANSACTION_TYPE'
SIS_SEQUENCE = 'SIS_SEQUENCE'
SMS_SEQUENCES = 'SMS_SEQUENCES'
SENDER = 'SENDER'
RECIPIENT = 'RECIPIENT'

logger = log.IntegrationAdaptorsLogger(__name__)


class WorkDescription(object):
    """A local copy of an instance of a work description from the state store"""

    def __init__(self, persistence_store: pa.PersistenceAdaptor, store_data: dict):
        """
        Given
        :param persistence_store:
        :param store_data:
        """
        if persistence_store is None:
            raise ValueError('Expected persistence store')

        self.persistence_store = persistence_store
        self._deserialize_data(store_data)

    async def publish(self):
        """
        Attempts to publish the local state of the work description to the state store, checks versions to avoid
        collisions
        :return:
        """
        logger.info(f'Attempting to publish work description {self.operation_id}')

        serialised = self._serialise_data()

        await self.persistence_store.add(self.operation_id, serialised)
        logger.info(f'Successfully updated work description to state store for {self.operation_id}')

    def _deserialize_data(self, store_data):
        data_attribute = store_data['DATA']
        self.operation_id: str = store_data.get('OPERATION_ID')
        self.transaction_id: int = data_attribute.get('TRANSACTION_ID')
        self.transaction_timestamp: str = data_attribute.get('TRANSACTION_TIMESTAMP')
        self.transaction_type: str = data_attribute.get('TRANSACTION_TYPE')
        self.sis_sequence: int = data_attribute.get('SIS_SEQUENCE')
        self.sms_sequences: list = data_attribute.get('SMS_SEQUENCES')
        self.sender: str = data_attribute.get('SENDER')
        self.recipient: str = data_attribute.get('RECIPIENT')

    def _serialise_data(self):
        """
        A simple serialization method that produces an object from the local data which can be stored in the
        persistence store
        """
        return {
            OPERATION_ID: self.operation_id,
            DATA: {
                TRANSACTION_ID: self.transaction_id,
                TRANSACTION_TIMESTAMP: self.transaction_timestamp,
                TRANSACTION_TYPE: self.transaction_type,
                SIS_SEQUENCE: self.sis_sequence,
                SMS_SEQUENCES: self.sms_sequences,
                SENDER: self.sender,
                RECIPIENT: self.recipient
            }
        }


def create_new_work_description(persistence_store: pa.PersistenceAdaptor,
                                operation_id: str,
                                transaction_id: int,
                                transaction_timestamp: str,
                                transaction_type: str,
                                sis_sequence: int,
                                sms_sequences: list,
                                sender: str,
                                recipient: str
                                ) -> WorkDescription:
    """
    Builds a new local work description instance given the details of the message, these details are held locally
    until a `publish` is executed
    """
    if persistence_store is None:
        raise ValueError('Expected persistence store to not be None')
    if not operation_id:
        raise ValueError('Expected operation_id to not be None or empty')
    if not transaction_id:
        raise ValueError('Expected transaction_id to not be None or empty')
    if not transaction_timestamp:
        raise ValueError('Expected transaction_timestamp to not be None or empty')
    if not transaction_type:
        raise ValueError('Expected transaction_type to not be None or empty')
    if not sis_sequence:
        raise ValueError('Expected sis_sequence to not be None or empty')
    if not sms_sequences:
        raise ValueError('Expected sms_sequences to not be None or empty')
    if not sender:
        raise ValueError('Expected sender to not be None or empty')
    if not recipient:
        raise ValueError('Expected recipient to not be None or empty')

    work_description_map = {
        OPERATION_ID: operation_id,
        DATA: {
            TRANSACTION_ID: transaction_id,
            TRANSACTION_TIMESTAMP: transaction_timestamp,
            TRANSACTION_TYPE: transaction_type,
            SIS_SEQUENCE: sis_sequence,
            SMS_SEQUENCES: sms_sequences,
            SENDER: sender,
            RECIPIENT: recipient
        }
    }

    return WorkDescription(persistence_store, work_description_map)
