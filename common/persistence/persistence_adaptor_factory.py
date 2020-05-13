import utilities.config as config
import utilities.integration_adaptors_logger as log
from persistence.dynamo_persistence_adaptor import DynamoPersistenceAdaptor
from persistence.mongo_persistence_adaptor import MongoPersistenceAdaptor
from persistence.persistence_adaptor import PersistenceAdaptor

logger = log.IntegrationAdaptorsLogger(__name__)

_DEFAULT_ADAPTOR = 'dynamodb'
PERSISTENCE_ADAPTOR_TYPES = {
    _DEFAULT_ADAPTOR: DynamoPersistenceAdaptor,
    'mongodb': MongoPersistenceAdaptor,
}


def get_persistence_adaptor(*args, **kwargs) -> PersistenceAdaptor:
    """
    Builds a new persistence adaptor of type defined in environment variable PERSISTENCE_ADAPTOR
    Must be one of the defined in mhs.common.state.persistence_adaptor_factory._PERSISTENCE_ADAPTOR_TYPES
    :class:`PersistenceAdaptor <mhs.common.state.persistence_adaptor.PersistenceAdaptor>`.
    :param args: passed downstream to persistence adaptor constructor
    :param kwargs: passed downstream to persistence adaptor constructor
    :return: new instance of persistence adaptor
    """
    persistence_adaptor = config.get_config('PERSISTENCE_ADAPTOR', default=_DEFAULT_ADAPTOR)
    logger.info("Building persistence adaptor using '%s' type", persistence_adaptor)
    return PERSISTENCE_ADAPTOR_TYPES[persistence_adaptor.lower()](*args, **kwargs)
