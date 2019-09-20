import json
import unittest


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
        json_string_value = self.item['data']['S']
        actual_values = json.loads(json_string_value)['DATA']

        for key in expected_values:
            expected_value = expected_values[key]
            actual_value = actual_values.get(key)

            self.assertor.assertEqual(expected_value, actual_value,
                                      f'Values not equal when comparing dictionary keys: {key}')


class DynamoMhsTableStateAssertor(object):
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
        items_with_key = [x for x in self.state['Items'] if x['key']['S'] == key]
        self.assertor.assertTrue(len(items_with_key) == 1,
                                 f'Expected an item with key: {key} but not exactly one found')
        return MhsItemAssertor(items_with_key[0])
