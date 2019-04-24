import unittest
from common.utilities import Utilities
from lxml import etree
from definitions import ROOT_DIR
from pathlib import Path
from scr.gpsummaryupdate import SummaryCareRecord


class FullTest(unittest.TestCase):

    summaryCareRecord = SummaryCareRecord()

    def test_basic(self):
        """
        A basic test using the clean summary update from the spine tests
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/cleanSummaryUpdate.xml'))
        expected = etree.tostring(root)
        render = self.summaryCareRecord.populate_template_with_file(
            str(Path(ROOT_DIR) / 'scr/tests/hashes/hash16UK05.json'))
        Utilities.assert_xml_equal(expected, render)

    def test_extended_html(self):
        """
        Uses a larger set of Html for the human readable contents
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/SummaryUpdateExtendedContents.xml'))
        expected = etree.tostring(root)

        file_path = str(Path(ROOT_DIR) / 'scr/tests/hashes/extendedHTMLhash.json')
        render = self.summaryCareRecord.populate_template_with_file(file_path)

        Utilities.assert_xml_equal(expected, render)

    def test_empty_html(self):
        """
        A test for an empty human readable content value
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/EmptyHtmlGpSummaryUpdate.xml'))
        expected = etree.tostring(root)

        file_path = str(Path(ROOT_DIR) / 'scr/tests/hashes/emptyHtmlHash.json')
        render = self.summaryCareRecord.populate_template_with_file(file_path)

        Utilities.assert_xml_equal(expected, render)

    def test_empty_hash(self):
        """
        Tests the contents are empty when a completely blank hash is provided
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/EmptyHash.xml'))
        expected = etree.tostring(root)

        file_path = str(Path(ROOT_DIR) / 'scr/tests/hashes/EmptyHash.json')
        render = self.summaryCareRecord.populate_template_with_file(file_path)
        Utilities.assert_xml_equal(expected, render)

    def test_replacementOf(self):
        """
        Note: this is not a valid xml instance
        This is to demonstrate the condition aspect of the replacementOf partial,
        this partial doesnt appear in the previous tests but here a list with a single
        element is used to show how conditionals are used in mustache
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/replacementOf.xml'))
        expected = etree.tostring(root)

        file_path = str(Path(ROOT_DIR) / 'scr/tests/hashes/replacementOfhash.json')
        render = self.summaryCareRecord.populate_template_with_file(file_path)
        Utilities.assert_xml_equal(expected, render)

    def test_multipleReplacementOf(self):
        """
        Note: THIS IS NOT A VALID XML INSTANCE
        This test is build purely for demonstrating having a variable number of occurrences of
        a partial in mustache, it does not conform to the schema and will not be accepted as a valid message
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/multipleReplacementOf.xml'))
        expected = etree.tostring(root)

        file_path = str(Path(ROOT_DIR) / 'scr/tests/hashes/multiReplacementOfhash.json')
        render = self.summaryCareRecord.populate_template_with_file(file_path)
        Utilities.assert_xml_equal(expected, render)

    def test_python_dictionary_example(self):
        """
        Basic test to demonstrate passing a python dict to the interface instead of a json file
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/cleanSummaryUpdate.xml'))
        expected = etree.tostring(root)
        from scr.tests.hashes.basic_dict import input_hash

        render = self.summaryCareRecord.populate_template(input_hash)
        Utilities.assert_xml_equal(expected, render)

    def test_json_string_example(self):
        """
        Basic example showing how a json string can be passed to the interface
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/cleanSummaryUpdate.xml'))
        expected = etree.tostring(root)
        json_file = str(Path(ROOT_DIR) / 'scr/tests/hashes/hash16UK05.json')
        with open(json_file) as file:
            data = file.read()  # Reads file contents into a string
            render = self.summaryCareRecord.populate_template_with_json_string(data)
            Utilities.assert_xml_equal(expected, render)
