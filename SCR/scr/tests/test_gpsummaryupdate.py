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

    templatePath = Path(ROOT_DIR) / "scr/16UK05.mustache"
    summaryCareRecord = SummaryCareRecord()

    def test_basic(self):
        root = etree.parse('./TestXmls/cleanSummaryUpdate.xml')
        expected = etree.tostring(root)

        render = self.summaryCareRecord.render_hash(hash)

        Utilities.assert_xml_equal(expected, render)

    def test_extended_html(self):
        root = etree.parse('./TestXmls/SummaryUpdateExtendedContents.xml')
        expected = etree.tostring(root)

        render = self.summaryCareRecord.render_hash(extended_hash)

        Utilities.assert_xml_equal(expected, render)

    def test_empty_html(self):
        root = etree.parse('./TestXmls/EmptyGpSummaryUpdate.xml')
        expected = etree.tostring(root)

        render = self.summaryCareRecord.render_hash(empty_hash)

        Utilities.assert_xml_equal(expected, render)

    def test_replacementOf(self):
        root = etree.parse('./TestXmls/replacementOf.xml')
        expected = etree.tostring(root)

        render = self.summaryCareRecord.render_hash(replacementOf_hash)
        Utilities.assert_xml_equal(expected, render)


    def test_multipleReplacementOf(self):
        """
        Note: THIS IS NOT A VALID XML INSTANCE
        This test is build purely for demonstrating having a variable number of occurrences of
        a partial in mustache, it does not conform to the schema and will not be accepted as a valid message
        """
        root = etree.parse('./TestXmls/multipleReplacementOf.xml')
        expected = etree.tostring(root)

        render = self.summaryCareRecord.render_hash(multi_replacementOf_hash)
        Utilities.assert_xml_equal(expected, render)