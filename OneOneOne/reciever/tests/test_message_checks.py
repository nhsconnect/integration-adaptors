import unittest
from pathlib import Path
from builder.pystache_message_builder import PystacheMessageBuilder
import xml.etree.ElementTree as ET
from definitions import ROOT_DIR
from reciever.message_checks.checks import *


class MessageCheckTests(unittest.TestCase):
    inputXmlFileDir = Path(ROOT_DIR) / 'reciever' / 'tests' / 'input_xmls'
    builder = PystacheMessageBuilder(str(inputXmlFileDir), 'base_input')

    def generate_message_tree(self, input_hash):
        msg = self.builder.build_message(input_hash)
        return ET.fromstring(msg)

    def test_action_not_matching_service(self):

        with self.subTest("Two differing services result in a 500 error"):
            service_dict = {'action': "urn:nhs-itk:services:201005:SendNHS111Report-v2-0-ThisDoesNotMatchBelow",
                            'service': "urn:nhs-itk:services:201005:SendNHS111Report-Bad_Service-ThisDoesNotMatchAbove"}

            fail_flag, response = CheckActionTypes(self.generate_message_tree(service_dict)).check()

            self.assertTrue(fail_flag)
            self.assertEqual("Manifest action does not match service action", response)

        with self.subTest("Two services which are the same should return 200 code"):
            service_dict = {'action': "urn:nhs-itk:services:201005:SendNHS111Report",
                            'service': "urn:nhs-itk:services:201005:SendNHS111Report"}

            fail_flag, response = CheckActionTypes(self.generate_message_tree(service_dict)).check()

            self.assertFalse(fail_flag)
            self.assertEqual(response, None)

    def test_manifest_payload_count(self):

        with self.subTest("Mismatched counts: 500 response"):
            counts = {'manifestCount': "2",
                      'payloadCount': "5"}
            fail_flag, response = CheckManifestPayloadCounts(self.generate_message_tree(counts)).check()

            self.assertTrue(fail_flag)
            self.assertEqual("Manifest count does not match payload count", response)

        with self.subTest("Equal counts: 200 response"):
            counts = {'manifestCount': "2",
                      'payloadCount': "2"}
            fail_flag, response = CheckManifestPayloadCounts(self.generate_message_tree(counts)).check()

            self.assertFalse(fail_flag)
            self.assertEqual(None, response)

    def test_manifest_count_matches_manifest_instances(self):

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            manifests = {'manifestCount': "2",
                         'manifests': [{"id": 'one'}]}
            fail_flag, response = CheckManifestCountInstances(self.generate_message_tree(manifests)).check()

            self.assertTrue(fail_flag)
            self.assertEqual("The number of manifest instances does not match the manifest count specified", response)

        with self.subTest("Correct manifest occurrences returns 500 error"):
            manifests = {'manifestCount': "1",
                         'manifests': [{"id": 'one'}]}

            fail_flag, response = CheckManifestCountInstances(self.generate_message_tree(manifests)).check()

            self.assertFalse(fail_flag)
            self.assertEqual(None, response)

    def test_payload_count_against_instances(self):

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            manifests = {'payloadCount': "2",
                         'payloads': [{"id": 'one'}]}
            fail_flag, response = CheckPayloadCountAgainstActual(self.generate_message_tree(manifests)).check()

            self.assertTrue(fail_flag)
            self.assertEqual("Invalid message", response)

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            manifests = {'payloadCount': "1",
                         'payloads': [{"id": 'one'}]}
            fail_flag, response = CheckPayloadCountAgainstActual(self.generate_message_tree(manifests)).check()

            self.assertFalse(fail_flag)
            self.assertEqual(None, response)

    def test_payload_id_matches_manifest_id(self):

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            dictionary = {'payloadCount': "2",
                          'payloads': [{"id": 'one'}, {"id": 'three'}],
                          'manifestCount': "2",
                          'manifests': [{"id": 'one'}, {"id": 'two'}]
                          }
            fail_flag, response = CheckPayloadIdAgainstManifestId(self.generate_message_tree(dictionary)).check()

            self.assertTrue(fail_flag)
            self.assertEqual("Payload IDs do not map to Manifest IDs", response)

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            dictionary = {'payloadCount': "2",
                          'payloads': [{"id": 'one'}],
                          'manifestCount': "2",
                          'manifests': [{"id": 'one'}]
                          }
            fail_flag, response = CheckPayloadIdAgainstManifestId(self.generate_message_tree(dictionary)).check()

            self.assertFalse(fail_flag)
            self.assertEqual(None, response)
