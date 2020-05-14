from typing import Optional
from unittest import TestCase
from unittest.mock import patch

from persistence.dynamo_persistence_adaptor import DynamoPersistenceAdaptor
import persistence.persistence_adaptor_factory as factory
from persistence.mongo_persistence_adaptor import MongoPersistenceAdaptor
from persistence.persistence_adaptor import PersistenceAdaptor


class FakePersistenceAdaptor(PersistenceAdaptor):
    def __init__(self, table_name):
        super().__init__()
        self.table_name = table_name

    async def add(self, key: str, data: dict) -> Optional[dict]:
        pass

    async def update(self, key: str, data: dict):
        pass

    async def get(self, key: str) -> Optional[dict]:
        pass

    async def delete(self, key: str) -> Optional[dict]:
        pass


class TestPersistenceAdaptorFactory(TestCase):
    _TYPES = {
        # fake one only for testing purpose
        'fake': FakePersistenceAdaptor,
        # add real adaptors below to match those defined in mhs_common.state.persistence_adaptor_factory
        'dynamodb': DynamoPersistenceAdaptor,
        'mongodb': MongoPersistenceAdaptor,
    }

    def setUp(self) -> None:
        super().setUp()
        factory.PERSISTENCE_ADAPTOR_TYPES['fake'] = FakePersistenceAdaptor

    def tearDown(self) -> None:
        super().tearDown()
        del factory.PERSISTENCE_ADAPTOR_TYPES['fake']

    def test_all_persistence_types_are_defined(self):
        self.assertEqual(self._TYPES.keys(), factory.PERSISTENCE_ADAPTOR_TYPES.keys())

    @patch('mhs_common.state.persistence_adaptor_factory.config')
    def test_get_all_types_of_persistence_adaptors(self, config):
        for persistence_adaptor_type in factory.PERSISTENCE_ADAPTOR_TYPES:
            config.get_config.return_value = persistence_adaptor_type

            adaptor = factory.get_persistence_adaptor(**{'table_name': 'foobar'})

            expected_type = self._TYPES[persistence_adaptor_type]
            actual_type = type(adaptor)
            self.assertEqual(actual_type, expected_type)
            self.assertTrue(issubclass(actual_type, PersistenceAdaptor))
