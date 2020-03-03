"""
Provides functionality to assert items within the MHS sync/async Dynamo table
"""
import json
import unittest

from integration_tests.xml.hl7_xml_assertor import Hl7XmlResponseAssertor


class DynamoSyncAsyncMhsTableStateAssertor(object):
    """
    A class that is able to assert records within the MHS sync/async table shape
    """

    def __init__(self, current_state: dict):
        """
        :param current_state: the records currently returned by Dynamo within the MHS sync/async table
        """
        self.state = current_state
        self.assertor = unittest.TestCase('__init__')

    def assert_single_item_exists_with_key(self, key: str) -> Hl7XmlResponseAssertor:
        """
        Asserts a single item exists within the MHS sync/async table with the given key
        :param key: the key to search for
        :return: an Hl7XmlResponseAssertor that can be used to the HL7 message within the table
        """
        items_with_key = [x for x in self.state['Items'] if x['key']['S'] == key]
        num_items = len(items_with_key)
        self.assertor.assertTrue(len(items_with_key) == 1, f'Expected exactly one item with key {key} '
                                                           f'but found {num_items}')

        json_string_value = items_with_key[0]['data']['S']
        xml_message = json.loads(json_string_value)['data']

        return Hl7XmlResponseAssertor(xml_message)

    def __str__(self):
        return f'{self.state}'
