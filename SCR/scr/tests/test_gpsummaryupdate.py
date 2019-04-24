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
        :return:
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/cleanSummaryUpdate.xml'))
        expected = etree.tostring(root)
        render = self.summaryCareRecord.populate_template_with_file(str(Path(ROOT_DIR) / 'scr/tests/hashes/hash16UK05.json'))
        Utilities.assert_xml_equal(expected, render)

    def test_extended_html(self):
        """
        Uses a larger set of Html for the human readable contents
        :return:
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/SummaryUpdateExtendedContents.xml'))
        expected = etree.tostring(root)

        file_path = str(Path(ROOT_DIR) / 'scr/tests/hashes/extendedHTMLhash.json')
        render = self.summaryCareRecord.populate_template_with_file(file_path)

        Utilities.assert_xml_equal(expected, render)

    def test_empty_html(self):
        """
        A test for an empty human readable content value
        :return:
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/EmptyGpSummaryUpdate.xml'))
        expected = etree.tostring(root)

        file_path = str(Path(ROOT_DIR) / 'scr/tests/hashes/emptyhash.json')
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

