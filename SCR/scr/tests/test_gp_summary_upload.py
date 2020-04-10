import unittest
from pathlib import Path
from builder.pystache_message_builder import MessageGenerationError
import utilities.file_utilities as file_utilities
from utilities.xml_utilities import XmlUtilities
from scr_definitions import ROOT_DIR
from scr.gp_summary_upload import GpSummaryUpload


class GpSummaryUploadTest(unittest.TestCase):
    gp_summary_upload_templator = GpSummaryUpload()

    xmlFileDir = Path(ROOT_DIR + '/scr/tests/test_xmls/')
    hashFileDir = Path(ROOT_DIR + '/scr/tests/hashes/')

    def test_basic(self):
        """
        A basic test using the clean summary update from the spine tests
        """
        expected_xml_file_path = str(self.xmlFileDir / 'cleanSummaryUpdate.xml')
        hash_file_path = str(self.hashFileDir / 'hash16UK05.json')

        expected_string = file_utilities.get_file_string(expected_xml_file_path)
        render = self.gp_summary_upload_templator.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_extended_html(self):
        """
        Uses a larger set of Html for the human readable contents
        """
        expected_xml_file_path = str(self.xmlFileDir / 'SummaryUpdateExtendedContents.xml')
        hash_file_path = str(self.hashFileDir / 'extendedHTMLhash.json')

        expected_string = file_utilities.get_file_string(expected_xml_file_path)
        render = self.gp_summary_upload_templator.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_empty_html(self):
        """
        A test for an empty human readable content value
        """
        expected_xml_file_path = str(self.xmlFileDir / 'EmptyHtmlGpSummaryUpdate.xml')
        hash_file_path = str(self.hashFileDir / 'emptyHtmlHash.json')

        expected_string = file_utilities.get_file_string(expected_xml_file_path)
        render = self.gp_summary_upload_templator.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_should_raise_exception_when_hash_is_empty(self):
        """
        Tests the contents are empty when a completely blank hash is provided
        """
        hash_file_path = str(self.hashFileDir / 'EmptyHash.json')

        with self.assertRaises(MessageGenerationError):
            self.gp_summary_upload_templator.populate_template_with_file(hash_file_path)

    def test_should_raise_exception_when_missing_element_in_input_dict(self):

        hash_file_path = str(self.hashFileDir / 'missingTag.json')

        with self.assertRaises(MessageGenerationError):
            self.gp_summary_upload_templator.populate_template_with_file(hash_file_path)

    def test_replacementOf(self):
        """
        Note: this is not a valid xml instance
        This is to demonstrate the condition aspect of the replacementOf partial,
        this partial doesnt appear in the previous tests but here a list with a single
        element is used to show how conditionals are used in mustache
        """
        expected_xml_file_path = str(self.xmlFileDir / 'replacementOf.xml')
        hash_file_path = str(self.hashFileDir / 'replacementOfhash.json')

        expected_string = file_utilities.get_file_string(expected_xml_file_path)
        render = self.gp_summary_upload_templator.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_multipleReplacementOf(self):
        """
        Note: THIS IS NOT A VALID XML INSTANCE
        This test is build purely for demonstrating having a variable number of occurrences of
        a partial in mustache, it does not conform to the schema and will not be accepted as a valid message
        """
        expected_xml_file_path = str(self.xmlFileDir / 'multipleReplacementOf.xml')
        hash_file_path = str(self.hashFileDir / 'multiReplacementOfhash.json')

        expected_string = file_utilities.get_file_string(expected_xml_file_path)
        render = self.gp_summary_upload_templator.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_python_dictionary_example(self):
        """
        Basic test to demonstrate passing a python dict to the interface instead of a json file
        """
        expected_string = file_utilities.get_file_string(
            str(Path(ROOT_DIR) / 'scr/tests/test_xmls/cleanSummaryUpdate.xml'))
        from scr.tests.hashes.basic_dict import input_hash

        render = self.gp_summary_upload_templator.populate_template(input_hash)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_json_string_example(self):
        """
        Basic example showing how a json string can be passed to the interface
        """
        expected_string = file_utilities.get_file_string(str(self.xmlFileDir / 'cleanSummaryUpdate.xml'))
        json_file = str(self.hashFileDir / 'hash16UK05.json')
        with open(json_file) as file:
            data = file.read()  # Reads file contents into a string
            render = self.gp_summary_upload_templator.populate_template_with_json_string(data)
            XmlUtilities.assert_xml_equal(expected_string, render)

    def test_should_return_success_response_with_valid_json(self):
        """
        Simple assertion of correct values returned from the response parsing method
        """
        input_xml = file_utilities.get_file_string(str(self.xmlFileDir / 'parseSuccessResponse.xml'))
        parsed_data = self.gp_summary_upload_templator.parse_response(input_xml)

        self.assertEqual(parsed_data['messageRef'], '9C534C19-C587-4463-9AED-B76F715D3EA3')
        self.assertEqual(parsed_data['messageId'], '2E372546-229A-483F-9B11-EF46ABF3178C')
        self.assertEqual(parsed_data['creationTime'], '20190923112609')
        self.assertEqual(parsed_data['messageDetail'], 'GP Summary upload successful')

    def test_should_return_error_when_there_is_a_bad_attribute_format(self):
        input_xml = file_utilities.get_file_string(str(self.xmlFileDir / 'badAttributeParse.xml'))
        parsed_data = self.gp_summary_upload_templator.parse_response(input_xml)

        self.assertEqual(parsed_data['error'], 'Failed to parse all the necessary elements from xml returned from MHS')

    def test_should_return_error_when_the_text_value_for_attribute_is_empty(self):
        input_xml = file_utilities.get_file_string(str(self.xmlFileDir / 'badTextAttribute.xml'))
        parsed_data = self.gp_summary_upload_templator.parse_response(input_xml)

        self.assertEqual(parsed_data['error'], 'Failed to parse all the necessary elements from xml returned from MHS')

    def test_should_return_error_when_required_details_tag_is_missing(self):
        input_xml = file_utilities.get_file_string(str(self.xmlFileDir / 'missingAttribute.xml'))
        parsed_data = self.gp_summary_upload_templator.parse_response(input_xml)

        self.assertEqual(parsed_data['error'], 'Failed to parse all the necessary elements from xml returned from MHS')

    def test_should_return_error_when_required_creationTime_tag_is_missing(self):
        input_xml = file_utilities.get_file_string(str(self.xmlFileDir / 'missingAttribute.xml'))
        parsed_data = self.gp_summary_upload_templator.parse_response(input_xml)

        self.assertEqual(parsed_data['error'], 'Failed to parse all the necessary elements from xml returned from MHS')