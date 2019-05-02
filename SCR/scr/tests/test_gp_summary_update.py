import unittest
from pathlib import Path

from utilities.file_utilities import FileUtilities
from utilities.xml_utilities import XmlUtilities

from definitions import ROOT_DIR
from scr.gp_summary_update import SummaryCareRecord


class FullTest(unittest.TestCase):
    summaryCareRecord = SummaryCareRecord()

    xmlFileDir = Path(ROOT_DIR + '/scr/tests/test_xmls/')
    hashFileDir = Path(ROOT_DIR + '/scr/tests/hashes/')

    def test_basic(self):
        """
        A basic test using the clean summary update from the spine tests
        """
        expected_xml_file_path = str(self.xmlFileDir / 'cleanSummaryUpdate.xml')
        hash_file_path = str(self.hashFileDir / 'hash16UK05.json')

        expected_string = FileUtilities.get_file_string(expected_xml_file_path)
        render = self.summaryCareRecord.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_extended_html(self):
        """
        Uses a larger set of Html for the human readable contents
        """
        expected_xml_file_path = str(self.xmlFileDir / 'SummaryUpdateExtendedContents.xml')
        hash_file_path = str(self.hashFileDir / 'extendedHTMLhash.json')

        expected_string = FileUtilities.get_file_string(expected_xml_file_path)
        render = self.summaryCareRecord.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_empty_html(self):
        """
        A test for an empty human readable content value
        """
        expected_xml_file_path = str(self.xmlFileDir / 'EmptyHtmlGpSummaryUpdate.xml')
        hash_file_path = str(self.hashFileDir / 'emptyHtmlHash.json')

        expected_string = FileUtilities.get_file_string(expected_xml_file_path)
        render = self.summaryCareRecord.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_empty_hash(self):
        """
        Tests the contents are empty when a completely blank hash is provided
        """
        expected_xml_file_path = str(self.xmlFileDir / 'EmptyHash.xml')
        hash_file_path = str(self.hashFileDir / 'EmptyHash.json')

        expected_string = FileUtilities.get_file_string(expected_xml_file_path)
        render = self.summaryCareRecord.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_replacementOf(self):
        """
        Note: this is not a valid xml instance
        This is to demonstrate the condition aspect of the replacementOf partial,
        this partial doesnt appear in the previous tests but here a list with a single
        element is used to show how conditionals are used in mustache
        """
        expected_xml_file_path = str(self.xmlFileDir / 'replacementOf.xml')
        hash_file_path = str(self.hashFileDir / 'replacementOfhash.json')

        expected_string = FileUtilities.get_file_string(expected_xml_file_path)
        render = self.summaryCareRecord.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_multipleReplacementOf(self):
        """
        Note: THIS IS NOT A VALID XML INSTANCE
        This test is build purely for demonstrating having a variable number of occurrences of
        a partial in mustache, it does not conform to the schema and will not be accepted as a valid message
        """
        expected_xml_file_path = str(self.xmlFileDir / 'multipleReplacementOf.xml')
        hash_file_path = str(self.hashFileDir / 'multiReplacementOfhash.json')

        expected_string = FileUtilities.get_file_string(expected_xml_file_path)
        render = self.summaryCareRecord.populate_template_with_file(hash_file_path)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_python_dictionary_example(self):
        """
        Basic test to demonstrate passing a python dict to the interface instead of a json file
        """
        expected_string = FileUtilities.get_file_string(
            str(Path(ROOT_DIR) / 'scr/tests/test_xmls/cleanSummaryUpdate.xml'))
        from scr.tests.hashes.basic_dict import input_hash

        render = self.summaryCareRecord.populate_template(input_hash)
        XmlUtilities.assert_xml_equal(expected_string, render)

    def test_json_string_example(self):
        """
        Basic example showing how a json string can be passed to the interface
        """
        expected_string = FileUtilities.get_file_string(str(self.xmlFileDir / 'cleanSummaryUpdate.xml'))
        json_file = str(self.hashFileDir / 'hash16UK05.json')
        with open(json_file) as file:
            data = file.read()  # Reads file contents into a string
            render = self.summaryCareRecord.populate_template_with_json_string(data)
            XmlUtilities.assert_xml_equal(expected_string, render)
