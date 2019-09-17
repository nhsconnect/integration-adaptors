from unittest import TestCase

from integration_tests.helpers import methods
import xml.etree.ElementTree as ET


class SynchronousWorkflowTests(TestCase):

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
