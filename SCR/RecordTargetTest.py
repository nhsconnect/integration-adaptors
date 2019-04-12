import unittest
from pystache import Renderer

from lxml import etree
from lxml import objectify



class RecordTargetTest(unittest.TestCase):
    renderer = Renderer()

    _recordTargetTemplate = """<recordTarget typeCode="RCT" >
            <patient classCode="PAT">
                {{#recordTarget.InfrastructureRootElements}}
                    {{#realmCode}}
                        <realmCode value="{{realmCode}}"/>
                    {{/realmCode}}
                    {{#typeId}}
                        <typeId value="{{typeId}}"/> 
                    {{/typeId}}
                    {{#templateId}}
                        <templateId value="{{templateId}}"/>
                    {{/templateId}}
                {{/recordTarget.InfrastructureRootElements}}
                <id root="{{recordTarget.Patient.Id}}" extension="9900004948"/>
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
                </patient>
            </recordTarget>
        """

        render = self.renderer.render(self._recordTargetTemplate, hash)
        self.assertXmlStringsEqual(expected, render)

    def test_realmCode(self):
        hash = {
            'variable': 'qweqwe', 
            'recordTarget': {
                'Patient': {
                    'Id': '2.16.840.1.113883.2.1.4.1'
                },
                'InfrastructureRootElements': [
                    { 'realmCode': [
                        {'realmCode': 'qweqweqwe'}
                    ]}
                ]
            }
        }

        expected = """<recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <realmCode value="qweqweqwe"/>
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                </patient>
            </recordTarget>
        """

        render = self.renderer.render(self._recordTargetTemplate, hash)
        
        self.assertXmlStringsEqual(expected, render)

    def test_multiRealmCode(self):
        hash = {
            'variable': 'qweqwe', 
            'recordTarget': {
                'Patient': {
                    'Id': '2.16.840.1.113883.2.1.4.1'
                },
                'InfrastructureRootElements': [
                    { 'realmCode': [
                        {'realmCode': 'realmCode001'},
                        {'realmCode': 'realmCode002'},
                        {'realmCode': 'realmCode003'},
                        {'realmCode': 'realmCode004'}
                    ]}
                ]
            }
        }

        expected = """<recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <realmCode value="realmCode001"/>
                    <realmCode value="realmCode002"/>
                    <realmCode value="realmCode003"/>
                    <realmCode value="realmCode004"/>
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                </patient>
            </recordTarget>
        """

        render = self.renderer.render(self._recordTargetTemplate, hash)
        
        self.assertXmlStringsEqual(expected, render)

    def test_typeId(self):
        hash = {
            'variable': 'qweqwe', 
            'recordTarget': {
                'Patient': {
                    'Id': '2.16.840.1.113883.2.1.4.1'
                },
                'InfrastructureRootElements': [
                    { 'typeId': [
                        {'typeId': '1.20222.2012.123'}
                    ]}
                ]
            }
        }

        expected = """<recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <typeId value="1.20222.2012.123"/>
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                </patient>
            </recordTarget>
        """

        render = self.renderer.render(self._recordTargetTemplate, hash)
        
        self.assertXmlStringsEqual(expected, render)

    def test_templateId(self):
        hash = {
            'variable': 'qweqwe', 
            'recordTarget': {
                'Patient': {
                    'Id': '2.16.840.1.113883.2.1.4.1'
                },
                'InfrastructureRootElements': [
                    { 'templateId': [
                        {'templateId': '1.20222.2012.123'}
                    ]}
                ]
            }
        }

        expected = """<recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <templateId value="1.20222.2012.123"/>
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                </patient>
            </recordTarget>
        """

        render = self.renderer.render(self._recordTargetTemplate, hash)
        
        self.assertXmlStringsEqual(expected, render)

    def test_multiTemplateId(self):
        hash = {
            'variable': 'qweqwe', 
            'recordTarget': {
                'Patient': {
                    'Id': '2.16.840.1.113883.2.1.4.1'
                },
                'InfrastructureRootElements': [
                    { 'templateId': [
                        {'templateId': 'code0001'},
                        {'templateId': 'code0002'},
                        {'templateId': 'code0003'},
                        {'templateId': 'code0004'}
                    ]}
                ]
            }
        }

        expected = """<recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <templateId value="code0001"/>
                    <templateId value="code0002"/>
                    <templateId value="code0003"/>
                    <templateId value="code0004"/>
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                </patient>
            </recordTarget>
        """

        render = self.renderer.render(self._recordTargetTemplate, hash)
        
        self.assertXmlStringsEqual(expected, render)

    def test_allInfrastructureRootElements(self):
        hash = {
            'variable': 'qweqwe', 
            'recordTarget': {
                'Patient': {
                    'Id': '2.16.840.1.113883.2.1.4.1'
                },
                'InfrastructureRootElements': [
                    { 'realmCode': [{'realmCode': '1.20222.2012.123'}]},
                    { 'typeId': [{'typeId': '1.20222.2012.123'}]},
                    { 'templateId': [{'templateId': '1.20222.2012.123'}]}
                ]
            }
        }

        expected = """<recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <realmCode value="1.20222.2012.123"/>
                    <typeId value="1.20222.2012.123"/>
                    <templateId value="1.20222.2012.123"/>
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                </patient>
            </recordTarget>
        """

        render = self.renderer.render(self._recordTargetTemplate, hash)
        
        self.assertXmlStringsEqual(expected, render)

    def test_multiAllInfrastructureRootElements(self):
        hash = {
            'variable': 'qweqwe', 
            'recordTarget': {
                'Patient': {
                    'Id': '2.16.840.1.113883.2.1.4.1'
                },
                'InfrastructureRootElements': [
                    { 'realmCode': [{'realmCode': 'realm001'}, {'realmCode': 'realm002'} ]},
                    { 'typeId': [{'typeId': '1.20222.2012.123'}]},
                    { 'templateId': [{'templateId': 'template001'}, {'templateId': 'template002'}]}
                ]
            }
        }

        expected = """<recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <realmCode value="realm001"/>
                    <realmCode value="realm002"/>
                    <typeId value="1.20222.2012.123"/>
                    <templateId value="template001"/>
                    <templateId value="template002"/>
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
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

        #print(expected)
        #print("----------------")
        #print(actual)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()