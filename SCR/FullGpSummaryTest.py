import unittest
from pystache import Renderer
from XmlHelper import XmlHelper
from lxml import etree
from hashes.hash16UK05 import hash
from hashes.extendedHTMLhash import extended_hash
from hashes.emptyhash import empty_hash


class FullTest(unittest.TestCase):
    renderer = Renderer()
    templatePath = "16UK05.mustache"


    def test_basic(self):

        root = etree.parse('./TestXmls/cleanSummaryUpdate.xml')
        expected = etree.tostring(root)


        render = self.renderer.render_path(self.templatePath, hash)

        XmlHelper.assertXmlStringsEqual(expected, render)


    def test_extended_html(self):
        root = etree.parse('./TestXmls/SummaryUpdateExtendedContents.xml')
        expected = etree.tostring(root)

        render = self.renderer.render_path(self.templatePath, extended_hash)

        XmlHelper.assertXmlStringsEqual(expected, render)

    def test_empty_html(self):
        root = etree.parse('./TestXmls/EmptyGpSummaryUpdate.xml')
        expected = etree.tostring(root)

        render = self.renderer.render_path(self.templatePath, empty_hash)

        XmlHelper.assertXmlStringsEqual(expected, render)