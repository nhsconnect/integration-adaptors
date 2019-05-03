import unittest
from pathlib import Path

from builder.pystache_message_builder import PystacheMessageBuilder
from utilities.file_utilities import FileUtilities
from utilities.xml_utilities import XmlUtilities
from OneOneOne.OneOneOne.message_handler import MessageHandler

from definitions import ROOT_DIR


class MessageHandlerTest(unittest.TestCase):
    expectedXmlFileDir = Path(ROOT_DIR) / 'OneOneOne' / 'tests' / 'expected_output_xmls'
    inputXmlFileDir = Path(ROOT_DIR) / 'OneOneOne' / 'tests' / 'input_xmls'

    def test_action_not_matching_service(self):
        builder = PystacheMessageBuilder(str(self.inputXmlFileDir), 'action_does_not_match_service')

        input = {'action': "urn:nhs-itk:services:201005:SendNHS111Report-v2-0-ThisDoesNotMatchBelow",
                 'service': "urn:nhs-itk:services:201005:SendNHS111Report-v2-0_Bad_Service-ThisDoesNotMatchAbove"}

        msg = builder.build_message(input)
        mh = MessageHandler(msg)
        status_code, response = mh.evaluate_message()

        assert (status_code == 500)

        expected = FileUtilities.get_file_string(
            str(self.expectedXmlFileDir / 'invalid_action_service_values_response.xml'))
        XmlUtilities.assert_xml_equal_utf_8(expected, response)

    def test_manifest_payload_count(self):
        builder = PystacheMessageBuilder(str(self.inputXmlFileDir), 'manifest_payload_count')

        input = {'manifestCount': "2",
                 'service': "5"}

        msg = builder.build_message(input)
        mh = MessageHandler(msg)
        status_code, response = mh.evaluate_message()

        assert (status_code == 500)

        expected = FileUtilities.get_file_string(
            str(self.expectedXmlFileDir / 'manifest_not_equal_to_payload_count.xml'))
        XmlUtilities.assert_xml_equal_utf_8(expected, response)

    def test_manifest_count_matches_manifest_instances(self):
        builder = PystacheMessageBuilder(str(self.inputXmlFileDir), 'manifest_payload_count')

        input = {'manifestCount': "2",
                 'manifest': ['one', 'two']}

        msg = builder.build_message(input)
        mh = MessageHandler(msg)
        status_code, response = mh.evaluate_message()

        assert (status_code == 500)

        expected = FileUtilities.get_file_string(
            str(self.expectedXmlFileDir / 'manifest_not_equal_to_payload_count.xml'))
        XmlUtilities.assert_xml_equal_utf_8(expected, response)