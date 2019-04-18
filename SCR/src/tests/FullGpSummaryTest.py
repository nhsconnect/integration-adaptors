import unittest

from common.utilities import Utilities
from lxml import etree
from src.tests.hashes.hash16UK05 import hash
from src.tests.hashes.extendedHTMLhash import extended_hash
from src.tests.hashes.emptyhash import empty_hash
from definitions import ROOT_DIR
from pathlib import Path
from src.SummaryCareRecord import SummaryCareRecord


class FullTest(unittest.TestCase):

    templatePath = Path(ROOT_DIR) / "src/16UK05.mustache"
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
