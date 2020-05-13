import unittest
from unittest.mock import patch
import uuid

from persistence.persistence_adaptor import PersistenceAdaptor
from persistence.persistence_adaptor_factory import get_persistence_adaptor, PERSISTENCE_ADAPTOR_TYPES
from utilities import test_utilities

MONGODB_ENDPOINT_URL = 'mongodb://localhost:27017'
DYNAMODB_ENDPOINT_URL = 'http://localhost:8000'
TEST_TABLE_NAME = "mhs_state"
SAMPLE_DATA = {
    "test-key1": "test-value1",
    "test-key2": "test-value2"
}
UPDATE_STATEMENT = {
    "test-key1": "updated-test-value1",
    "test-key3": "test-value3"
}
UPDATED_SAMPLE_DATA = {
    "test-key1": "updated-test-value1",
    "test-key2": "test-value2",
    "test-key3": "test-value3"
}
OTHER_DATA = {
    "other-key": "other-value"
}

DB_KEY_FIELDS = {
    'dynamodb': 'key',
    'mongodb': '_id',
}


class DbAdaptorsTests(unittest.TestCase):

    keys = []

    def setUp(self) -> None:
        self.clean_up()

    def tearDown(self) -> None:
        self.clean_up()

    def clean_up(self):
        for adaptor_type in PERSISTENCE_ADAPTOR_TYPES:
            for key in self.keys:
                adaptor = self.get_adaptor(adaptor_type)
                adaptor.delete(key)
        self.keys = []

    @test_utilities.async_test
    async def test_can_CRUD(self):
        for adaptor_type in PERSISTENCE_ADAPTOR_TYPES:
            with self.subTest(f"{adaptor_type}"):
                adaptor = self.get_adaptor(adaptor_type)

                key = str(uuid.uuid4()).upper()
                other_key = str(uuid.uuid4()).upper()
                self.keys += [key, other_key]

                await adaptor.add(other_key, OTHER_DATA)

                value = await adaptor.get(key)
                self.assertIsNone(value)

                await adaptor.add(key, SAMPLE_DATA)

                value = await adaptor.get(key)
                self.assertEqual(value, SAMPLE_DATA)

                value = await adaptor.update(key, UPDATE_STATEMENT)
                self.assertEqual(value, UPDATED_SAMPLE_DATA)

                value = await adaptor.get(key)
                self.assertEqual(value, UPDATED_SAMPLE_DATA)

                value = await adaptor.delete(key)
                self.assertEqual(value, UPDATED_SAMPLE_DATA)

                value = await adaptor.get(key)
                self.assertIsNone(value)

                value = await adaptor.get(other_key)
                self.assertEqual(value, OTHER_DATA)

                value = await adaptor.delete(other_key)
                self.assertEqual(value, OTHER_DATA)

                value = await adaptor.get(other_key)
                self.assertIsNone(value)

    @test_utilities.async_test
    async def test_error_if_data_to_add_has_primary_key_in(self):
        await self._test_error_if_data_has_primary_key_in(PersistenceAdaptor.add.__name__)

    @test_utilities.async_test
    async def test_error_if_data_to_update_has_primary_key_in(self):
        await self._test_error_if_data_has_primary_key_in(PersistenceAdaptor.update.__name__)

    async def _test_error_if_data_has_primary_key_in(self, func):
        for adaptor_type in PERSISTENCE_ADAPTOR_TYPES:
            with self.subTest(f"{adaptor_type}"):
                adaptor = self.get_adaptor(adaptor_type)

                key = str(uuid.uuid4()).upper()
                self.keys += key

                db_key_field = DB_KEY_FIELDS[adaptor_type]

                expected_error_message = f"Data must not have field named '{db_key_field}' as it's used " \
                                         f"as primary key and is explicitly set as this function argument"

                with self.assertRaisesRegex(ValueError, expected_error_message):
                    await getattr(adaptor, func)(key, {db_key_field: "some_value"})

    @staticmethod
    def get_adaptor(adaptor_type, max_retries=0, retry_delay=0):
        with patch('persistence.persistence_adaptor_factory.config') as factory_config,\
                patch('persistence.mongo_persistence_adaptor.config') as mongo_config,\
                patch('persistence.dynamo_persistence_adaptor.config') as dynamo_config:
            factory_config.get_config.return_value = adaptor_type
            mongo_config.get_config.return_value = MONGODB_ENDPOINT_URL
            dynamo_config.get_config.return_value = DYNAMODB_ENDPOINT_URL
            return get_persistence_adaptor(table_name=TEST_TABLE_NAME, max_retries=max_retries, retry_delay=retry_delay)
