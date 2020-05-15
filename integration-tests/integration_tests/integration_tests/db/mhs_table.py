"""
Provides functionality to assert items within the MHS Dynamo table
"""
import unittest

from integration_tests.db.db_wrapper_factory import MHS_STATE_TABLE_WRAPPER, KEY_NAME


class MhsItemAssertor(object):
    """
    A class that can assert properties over the shape of a single item stored within the MHS table
    """

    def __init__(self, item: dict):
        """
        :param item: the item from the MHS table that you wish to assert properties on
        """
        self.item = item
        self.assertor = unittest.TestCase('__init__')

    def assert_item_contains_values(self, expected_values: dict) -> None:
        """
        Asserts that the item's data property contains each of the expected values.
        :param expected_values: the key/values within the data property of the item you wish to assert
        :return: None
        """
        for key in expected_values:
            expected_value = expected_values[key]
            actual_value = self.item.get(key)

            self.assertor.assertEqual(expected_value, actual_value,
                                      f'Values not equal when comparing dictionary keys: {key}')

    def item_contains_value(self, expected_key: str, expected_value) -> bool:
        return expected_value == self.item.get(expected_key)


class MhsTableStateAssertor(object):
    """
    A class that is able to assert records within the MHS table shape
    """

    def __init__(self, current_state: dict):
        """
        :param current_state: the records currently returned by Dynamo within the MHS table
        """
        self.state = current_state
        self.assertor = unittest.TestCase('__init__')

    def assert_single_item_exists_with_key(self, key: str) -> MhsItemAssertor:
        """
        Asserts a single item exists within the MHS with the given key
        :param key: the key to search for
        :return: an MhsItemAssertor that can be used to assert properties on the given item
        """
        items_with_key = list(filter(lambda d: d[KEY_NAME] == key, self.state))
        num_items = len(items_with_key)
        self.assertor.assertTrue(len(items_with_key) == 1, f'Expected exactly one item with key {key} '
                                                           f'but found {num_items}')
        return MhsItemAssertor(items_with_key[0])

    @staticmethod
    def wait_for_inbound_response_processed(message_id: str) -> bool:
        return MhsTableStateAssertor(MHS_STATE_TABLE_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .item_contains_value('INBOUND_STATUS', 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED')

    def __str__(self):
        return f'{self.state}'
