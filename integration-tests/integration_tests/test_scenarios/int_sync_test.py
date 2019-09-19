import xml.etree.ElementTree as ET
from unittest import TestCase

from integration_tests.dynamo.dynamo import MHS_DYNAMO_WRAPPER
from integration_tests.dynamo.dynamo_mhs_table import DynamoMhsTableStateAssertor
from integration_tests.helpers import methods
from integration_tests.helpers.build_message import build_message
from integration_tests.helpers.methods import get_asid
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder


class SynchronousWorkflowTests(TestCase):

    def setUp(self):
        MHS_DYNAMO_WRAPPER.clear_all_records_in_table()

    def test_should_record_synchronous_message_status_as_successful(self):
        # Arrange
        message, message_id = build_message('QUPA_IN040000UK32', get_asid(), '9689174606', 'Synchronous test')

        # Act
        MhsHttpRequestBuilder() \
            .with_headers(interaction_id='QUPA_IN040000UK32', message_id=message_id, sync_async=False) \
            .with_body(message) \
            .execute_post_expecting_success()

        # Assert
        DynamoMhsTableStateAssertor(MHS_DYNAMO_WRAPPER.get_all_records_in_table()) \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values({
                'INBOUND_STATUS': None,
                'OUTBOUND_STATUS': 'SYNC_RESPONSE_SUCCESSFUL',
                'WORKFLOW': 'sync'
            })

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
