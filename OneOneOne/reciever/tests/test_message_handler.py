import unittest
from pathlib import Path
from builder.pystache_message_builder import PystacheMessageBuilder
from reciever.message_handler import MessageHandler
from utilities.file_utilities import FileUtilities
from utilities.xml_utilities import XmlUtilities
from OneOneOne.definitions import ROOT_DIR


class MessageHandlerTest(unittest.TestCase):
    expectedXmlFileDir = Path(ROOT_DIR) / 'reciever' / 'tests' / 'expected_output_xmls'
    inputXmlFileDir = Path(ROOT_DIR) / 'reciever' / 'tests' / 'input_xmls'

    builder = PystacheMessageBuilder(str(inputXmlFileDir), 'base_input')
    success_response = FileUtilities.get_file_string(str(expectedXmlFileDir / 'basic_success_response.xml'))

    def test_action_not_matching_service(self):
        with self.subTest("Two differing services result in a 500 error"):
            service_dict = {'action': "urn:nhs-itk:services:201005:SendNHS111Report-v2-0-ThisDoesNotMatchBelow",
                            'service': "urn:nhs-itk:services:201005:SendNHS111Report-Bad_Service-ThisDoesNotMatchAbove",
                            'manifestCount': 0,
                            'payloadCount': 0
                            }

            expected = FileUtilities.get_file_string(
                str(self.expectedXmlFileDir / 'invalid_action_service_values_response.xml'))

            msg = self.builder.build_message(service_dict)
            message_handler = MessageHandler(msg)

            self.assertEqual(message_handler.error_flag, True)
            XmlUtilities.assert_xml_equal_utf_8(expected, message_handler.get_response())

        with self.subTest("Two services which are the same should return 200 code"):
            service_dict = {'action': "urn:nhs-itk:services:201005:SendNHS111Report",
                            'service': "urn:nhs-itk:services:201005:SendNHS111Report",
                            'manifestCount': 0,
                            'payloadCount': 0
                            }

            msg = self.builder.build_message(service_dict)
            message_handler = MessageHandler(msg)

            self.assertEqual(message_handler.error_flag, False)
            XmlUtilities.assert_xml_equal_utf_8(self.success_response, message_handler.get_response())

    def test_manifest_payload_count(self):
        with self.subTest("Mismatched counts: 500 response"):
            counts = {
                'action': "urn:nhs-itk:services:201005:SendNHS111Report",
                'service': "urn:nhs-itk:services:201005:SendNHS111Report",
                'manifestCount': "1",
                'manifests': [{"id": 'one'}],
                'payloadCount': "2",
                'payloads': [{"id": 'one'}, {'id': "two"}]
            }

            expected = FileUtilities.get_file_string(
                str(self.expectedXmlFileDir / 'manifest_not_equal_to_payload_count.xml'))

            msg = self.builder.build_message(counts)
            message_handler = MessageHandler(msg)

            self.assertEqual(message_handler.error_flag, True)
            XmlUtilities.assert_xml_equal_utf_8(expected, message_handler.get_response())

        with self.subTest("Equal counts: 200 response"):
            counts = {
                'action': "urn:nhs-itk:services:201005:SendNHS111Report",
                'service': "urn:nhs-itk:services:201005:SendNHS111Report",
                'manifestCount': "2",
                'manifests': [{"id": 'one'}, {"id": "two"}],
                'payloadCount': "2",
                'payloads': [{"id": 'one'}, {'id': "two"}]
            }

            msg = self.builder.build_message(counts)
            message_handler = MessageHandler(msg)

            self.assertEqual(message_handler.error_flag, False)
            XmlUtilities.assert_xml_equal_utf_8(self.success_response, message_handler.get_response())

    def test_payload_id_matches_manifest_id(self):
        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            dictionary = {
                'action': "urn:nhs-itk:services:201005:SendNHS111Report",
                'service': "urn:nhs-itk:services:201005:SendNHS111Report",
                'manifestCount': "2",
                'manifests': [{"id": 'one'}, {'id': 'one'}],
                'payloadCount': "2",
                'payloads': [{"id": 'one'}, {'id': "two"}]
            }
            expected = FileUtilities.get_file_string(
                str(self.expectedXmlFileDir / 'payloadID_does_not_match_manifestID.xml'))

            msg = self.builder.build_message(dictionary)
            message_handler = MessageHandler(msg)

            self.assertEqual(message_handler.error_flag, True)
            XmlUtilities.assert_xml_equal_utf_8(expected, message_handler.get_response())

        with self.subTest("Incorrect manifest occurrences returns 500 error"):
            dictionary = {
                'action': "urn:nhs-itk:services:201005:SendNHS111Report",
                'service': "urn:nhs-itk:services:201005:SendNHS111Report",
                'manifestCount': "2",
                'manifests': [{"id": 'one'}, {'id': "two"}],
                'payloadCount': "2",
                'payloads': [{"id": 'one'}, {'id': "two"}]
            }

            msg = self.builder.build_message(dictionary)
            message_handler = MessageHandler(msg)

            self.assertEqual(message_handler.error_flag, False)
            XmlUtilities.assert_xml_equal_utf_8(self.success_response, message_handler.get_response())
