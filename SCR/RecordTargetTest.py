import unittest
from pystache import Renderer

from lxml import etree
from lxml import objectify



class RecordTargetTest(unittest.TestCase):
    renderer = Renderer()

    _recordTargetTemplate = """<recordTarget typeCode="RCT" >
            <patient classCode="PAT">
                <id root="{{recordTarget.Patient.Id}}" extension="9900004948"/>
                <!-- <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/> -->
            </patient>
        </recordTarget>
    """



    def test_basicRecordTestTempalte(self):
        self.assertTrue(True)

    def test_SimpleInput(self):
        hash = {
            'variable': 'qweqwe', 
            #'recordTarget.Patient.Id': '2.16.840.1.113883.2.1.4.1'
            'recordTarget': {
                'Patient': {
                    'Id': '2.16.840.1.113883.2.1.4.1'
                }
            }
        }

        expected = """<recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                    <!-- <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/> -->
                </patient>
            </recordTarget>
        """

        render = self.renderer.render(self._recordTargetTemplate, hash)
        self.assertXmlStringsEqual(expected, render)



    def assertXmlStringsEqual(self, expected, actual):
        obj1 = objectify.fromstring(expected)
        expected = etree.tostring(obj1)
        obj2 = objectify.fromstring(actual)
        actual = etree.tostring(obj2)

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()