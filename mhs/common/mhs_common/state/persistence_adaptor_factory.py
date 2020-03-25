import utilities.config as config
from mhs_common.state.dynamo_persistence_adaptor import DynamoPersistenceAdaptor
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

_DEFAULT_ADAPTOR = 'dynamodb'
_PERSISTENCE_ADAPTOR_TYPES = {
    _DEFAULT_ADAPTOR: DynamoPersistenceAdaptor,
}


def get_persistence_adaptor(*args, **kwargs):
    """
    Builds a new persistence adaptor of type defined in environment variable PERSISTENCE_ADAPTOR
    Must be one of the defined in mhs.common.state.persistence_adaptor_factory._PERSISTENCE_ADAPTOR_TYPES
    :class:`PersistenceAdaptor <mhs.common.state.persistence_adaptor.PersistenceAdaptor>`.
    :param args: passed downstream to persistence adaptor constructor
    :param kwargs: passed downstream to persistence adaptor constructor
    :return: new instance of persistence adaptor
    """
    persistence_adaptor = config.get_config('PERSISTENCE_ADAPTOR', default=_DEFAULT_ADAPTOR)
    logger.info("Building persistence adaptor using '{persistence_adaptor}' type",
                {'persistence_adaptor': persistence_adaptor})
    return _PERSISTENCE_ADAPTOR_TYPES[persistence_adaptor.lower()](*args, **kwargs)
