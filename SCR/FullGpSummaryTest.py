import unittest
from pystache import Renderer
from XmlHelper import XmlHelper
from lxml import etree
from hash16UK05 import hash

class FullTest(unittest.TestCase):
    renderer = Renderer()
    templatePath = "16UK05.mustache"


    def test_half_whole(self):
        #hash = 

        root = etree.parse('./cleanSummaryUpdate.xml')
        expected = etree.tostring(root)


        render = self.renderer.render_path(self.templatePath, hash)
        #print(render)

        XmlHelper.assertXmlStringsEqual(expected, render)
