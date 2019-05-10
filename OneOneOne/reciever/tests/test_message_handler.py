import unittest
from pathlib import Path
from builder.pystache_message_builder import PystacheMessageBuilder
from utilities.file_utilities import FileUtilities
from utilities.xml_utilities import XmlUtilities
import xml.etree.ElementTree as ET
from definitions import ROOT_DIR
from reciever.message_checks.checks import *


class MessageHandlerTest(unittest.TestCase):
    expectedXmlFileDir = Path(ROOT_DIR) / 'reciever' / 'tests' / 'expected_output_xmls'
    inputXmlFileDir = Path(ROOT_DIR) / 'reciever' / 'tests' / 'input_xmls'

    builder = PystacheMessageBuilder(str(inputXmlFileDir), 'base_input')
    success_response = FileUtilities.get_file_string(str(expectedXmlFileDir / 'basic_success_response.xml'))

    def test_action_not_matching_service(self):

        with self.subTest("Two differing services result in a 500 error"):
            service_dict = {'action': "urn:nhs-itk:services:201005:SendNHS111Report-v2-0-ThisDoesNotMatchBelow",
                            'service': "urn:nhs-itk:services:201005:SendNHS111Report-Bad_Service-ThisDoesNotMatchAbove"}

            expected = FileUtilities.get_file_string(
                str(self.expectedXmlFileDir / 'invalid_action_service_values_response.xml'))

            msg = self.builder.build_message(service_dict)
            message_tree = ET.fromstring(msg)
            mh = CheckActionTypes(message_tree)

            fail_flag, response = mh.check()

            self.assertTrue(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(expected, response)

        with self.subTest("Two services which are the same should return 200 code"):
            service_dict = {'action': "urn:nhs-itk:services:201005:SendNHS111Report",
                            'service': "urn:nhs-itk:services:201005:SendNHS111Report"}

            msg = self.builder.build_message(service_dict)
            message_tree = ET.fromstring(msg)
            mh = CheckActionTypes(message_tree)

            fail_flag, response = mh.check()

            self.assertFalse(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(self.success_response, response)

    def test_manifest_payload_count(self):

        with self.subTest("Mismatched counts: 500 response"):
            counts = {'manifestCount': "2",
                      'payloadCount': "5"}

            expected = FileUtilities.get_file_string(
                str(self.expectedXmlFileDir / 'manifest_not_equal_to_payload_count.xml'))

            msg = self.builder.build_message(counts)
            message_tree = ET.fromstring(msg)
            mh = CheckManifestPayloadCounts(message_tree)
            fail_flag, response = mh.check()

            self.assertTrue(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(expected, response)

        with self.subTest("Equal counts: 200 response"):
            counts = {'manifestCount': "2",
                      'payloadCount': "2"}

            msg = self.builder.build_message(counts)
            message_tree = ET.fromstring(msg)
            mh = CheckManifestPayloadCounts(message_tree)

            fail_flag, response = mh.check()

            self.assertFalse(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(self.success_response, response)

    def test_manifest_count_matches_manifest_instances(self):

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            manifests = {'manifestCount': "2",
                         'manifests': [{"id": 'one'}]}
            expected = FileUtilities.get_file_string(
                str(self.expectedXmlFileDir / 'invalid_manifest_instances.xml'))

            msg = self.builder.build_message(manifests)
            message_tree = ET.fromstring(msg)
            mh = CheckManifestCountInstances(message_tree)
            fail_flag, response = mh.check()

            self.assertTrue(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(expected, response)

        with self.subTest("Correct manifest occurrences returns 500 error"):
            manifests = {'manifestCount': "1",
                         'manifests': [{"id": 'one'}]}

            msg = self.builder.build_message(manifests)
            message_tree = ET.fromstring(msg)
            mh = CheckManifestCountInstances(message_tree)
            fail_flag, response = mh.check()

            self.assertFalse(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(self.success_response, response)

    def test_payload_count_against_instances(self):

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            manifests = {'payloadCount': "2",
                         'payloads': [{"id": 'one'}]}
            expected = FileUtilities.get_file_string(
                str(self.expectedXmlFileDir / 'basic_fault_response.xml'))

            msg = self.builder.build_message(manifests)
            message_tree = ET.fromstring(msg)
            mh = CheckPayloadCountAgainstActual(message_tree)
            fail_flag, response = mh.check()

            self.assertTrue(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(expected, response)

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            manifests = {'payloadCount': "1",
                         'payloads': [{"id": 'one'}]}

            msg = self.builder.build_message(manifests)
            message_tree = ET.fromstring(msg)
            mh = CheckPayloadCountAgainstActual(message_tree)
            fail_flag, response = mh.check()

            self.assertFalse(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(self.success_response, response)

    def test_payload_id_matches_manifest_id(self):

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            dictionary = {'payloadCount': "2",
                          'payloads': [{"id": 'one'}, {"id": 'three'}],
                          'manifestCount': "2",
                          'manifests': [{"id": 'one'}, {"id": 'two'}]
                          }
            expected = FileUtilities.get_file_string(
                str(self.expectedXmlFileDir / 'payloadID_does_not_match_manifestID.xml'))

            msg = self.builder.build_message(dictionary)
            message_tree = ET.fromstring(msg)
            mh = CheckPayloadIdAgainstManifestId(message_tree)
            fail_flag, response = mh.check()

            self.assertTrue(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(expected, response)

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            dictionary = {'payloadCount': "2",
                          'payloads': [{"id": 'one'}],
                          'manifestCount': "2",
                          'manifests': [{"id": 'one'}]
                          }

            msg = self.builder.build_message(dictionary)
            message_tree = ET.fromstring(msg)
            mh = CheckPayloadIdAgainstManifestId(message_tree)
            fail_flag, response = mh.check()

            self.assertFalse(fail_flag)
            XmlUtilities.assert_xml_equal_utf_8(self.success_response, response)
