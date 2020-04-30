import utilities.config as config
import utilities.integration_adaptors_logger as log

from sequence.dynamo_sequence import DynamoSequenceGenerator
from sequence.sequence import SequenceGenerator

logger = log.IntegrationAdaptorsLogger(__name__)

_DEFAULT_ADAPTOR = 'dynamodb'
_SEQUENCE_ADAPTOR_TYPES = {
    _DEFAULT_ADAPTOR: DynamoSequenceGenerator,
}


def get_sequence_generator(*args, **kwargs) -> SequenceGenerator:
    """
    Builds a new sequence adaptor of type defined in environment variable PERSISTENCE_ADAPTOR
    Must be one of the defined in _SEQUENCE_ADAPTOR_TYPES
    :class:`SequenceGenerator <sequence.sequence.SequenceGenerator>`.
    :param args: passed downstream to sequence adaptor constructor
    :param kwargs: passed downstream to sequence adaptor constructor
    :return: new instance of sequence generator
    """
    persistence_adaptor = config.get_config('PERSISTENCE_ADAPTOR', default=_DEFAULT_ADAPTOR)
    logger.info("Building sequence generator using '%s' type", persistence_adaptor)
    return _SEQUENCE_ADAPTOR_TYPES[persistence_adaptor.lower()](*args, **kwargs)
