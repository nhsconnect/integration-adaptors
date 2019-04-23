import unittest

from common.utilities import Utilities
from lxml import etree
from scr.tests.hashes.hash16UK05 import hash
from scr.tests.hashes.extendedHTMLhash import extended_hash
from scr.tests.hashes.emptyhash import empty_hash
from definitions import ROOT_DIR
from pathlib import Path
from scr.gpsummaryupdate import SummaryCareRecord
from scr.tests.hashes.replacementOfhash import replacementOf_hash

from scr.tests.hashes.multiReplacementOfhash import multi_replacementOf_hash


class FullTest(unittest.TestCase):

    summaryCareRecord = SummaryCareRecord()

    def test_basic(self):
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/cleanSummaryUpdate.xml'))
        expected = etree.tostring(root)

        render = self.summaryCareRecord.populate_template(hash)

        Utilities.assert_xml_equal(expected, render)

    def test_extended_html(self):
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/SummaryUpdateExtendedContents.xml'))
        expected = etree.tostring(root)

        render = self.summaryCareRecord.populate_template(extended_hash)

        Utilities.assert_xml_equal(expected, render)

    def test_empty_html(self):
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/EmptyGpSummaryUpdate.xml'))
        expected = etree.tostring(root)

        render = self.summaryCareRecord.populate_template(empty_hash)

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

        render = self.summaryCareRecord.populate_template(replacementOf_hash)
        Utilities.assert_xml_equal(expected, render)

    def test_multipleReplacementOf(self):
        """
        Note: THIS IS NOT A VALID XML INSTANCE
        This test is build purely for demonstrating having a variable number of occurrences of
        a partial in mustache, it does not conform to the schema and will not be accepted as a valid message
        """
        root = etree.parse(str(Path(ROOT_DIR) / 'scr/tests/test_xmls/multipleReplacementOf.xml'))
        expected = etree.tostring(root)

        render = self.summaryCareRecord.populate_template(multi_replacementOf_hash)
        Utilities.assert_xml_equal(expected, render)

