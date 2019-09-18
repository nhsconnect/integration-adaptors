import json
import unittest
from unittest import TestCase

import boto3
import requests

from integration_tests.helpers import methods
import xml.etree.ElementTree as ET

from integration_tests.helpers.build_message import build_message
from integration_tests.helpers.methods import get_asid


class DynamoDBWrapper(object):

    def __init__(self, **kwargs):
        self.dynamo_client = boto3.client('dynamodb', **kwargs)

    def get_all_records_in_table(self, table: str):
        return self.dynamo_client.scan(TableName=table)

    def clear_all_records_in_table(self, table: str):
        scan = self.get_all_records_in_table(table)

        for each in scan['Items']:
            self.dynamo_client.delete_item(TableName=table, Key={'key': {'S': each['key']['S']}})

class DyanmoStateAssertor(object):

    def __init__(self, current_state: dict):
        self.state = current_state
        self.assertor = unittest.TestCase('__init__')

    def assert_single_item_exists_with_key(self, key: str):
        items_with_key = [x for x in self.state['Items'] if x['key']['S'] == key]
        self.assertor.assertTrue(len(items_with_key) == 1, f'Expected an item with key: {key} but none found')
        return DictAssertor(items_with_key[0])

class DictAssertor(object):

    def __init__(self, item: dict):
        self.item = item
        self.assertor = unittest.TestCase('__init__')

    def assert_item_contains_values(self, expected_values: dict):
        json_string_value = self.item['data']['S']
        actual_values = json.loads(json_string_value)['DATA']

        for key in expected_values:
            expected_value = expected_values[key]
            actual_value = actual_values.get(key)

            self.assertor.assertEqual(expected_value, actual_value, f'Values not equal when comparing dictionary keys: {key}')


class SynchronousWorkflowTests(TestCase):

    # TODO:
    #  parameterise dynamo wrapper from env vars,
    #  add a before test hook to clear table for dynamo wrapper,
    #  provide clean abstraction for making web requests in tests
    #  make the dict assertor be specific to this table shape (rename)

    def test_should_record_synchronous_message_status_as_successful(self):
        # Arrange
        dynamo_wrapper = DynamoDBWrapper(region_name='eu-west-2', aws_access_key_id='anything',
                                         aws_secret_access_key='anything', endpoint_url='http://localhost:8000')
        dynamo_wrapper.clear_all_records_in_table(table='mhs_state')

        expected_recorded_state = {
            #'INBOUND_STATUS': None,
            'OUTBOUND_STATUS': 'SYNC_RESPONSE_SUCCESSFUL',
            'WORKFLOW': 'sync'
        }
        message, message_id = build_message('QUPA_IN040000UK32', get_asid(), '9689174606', 'Synchronous test')
        headers = {
            'Interaction-Id': 'QUPA_IN040000UK32',
            'Message-Id': message_id,
            'sync-async': 'false',
            'from-asid': f'{get_asid()}'
        }

        # Act
        result = requests.post(methods.get_mhs_hostname(), headers=headers, data=message)

        # Assert
        self.assertTrue(result.ok, f'A non successful error code was returned from server: {result.status_code}')
        DyanmoStateAssertor(dynamo_wrapper.get_all_records_in_table(table='mhs_state'))\
            .assert_single_item_exists_with_key(message_id)\
            .assert_item_contains_values(expected_recorded_state)

    def test_sync(self):
        mhs_response, _, _ = methods.get_interaction_from_template('synchronous',
                                                                   'QUPA_IN040000UK32',
                                                                   '9689174606',
                                                                   'Synchronous test')

        self.assertTrue(methods.check_response(mhs_response.text, 'PdsSuccessfulRetrieval'),
                        "Synchronous smoke test failed")

    def test_sync_patient_number(self):
        mhs_response, _, _ = methods.get_interaction_from_template('synchronous',
                                                                   'QUPA_IN040000UK32',
                                                                   '9689174606',
                                                                   'Synchronous test')

        root = ET.ElementTree(ET.fromstring(mhs_response.text)).getroot()
        element = root.find('.//hl7:patientRole/hl7:id', namespaces={'hl7': 'urn:hl7-org:v3'})
        self.assertEqual('9689174606', element.attrib['extension'])

    def test_sync_message_id(self):
        mhs_response, sent_message_id, _ = methods.get_interaction_from_template('synchronous',
                                                                                 'QUPA_IN040000UK32',
                                                                                 '9689174607',
                                                                                 'Synchronous test')

        root = ET.ElementTree(ET.fromstring(mhs_response.text)).getroot()
        element = root.find('.//hl7:messageRef/hl7:id', namespaces={'hl7': 'urn:hl7-org:v3'})

        self.assertEqual(sent_message_id, element.attrib['root'])
