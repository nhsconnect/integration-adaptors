import unittest
from pystache import Renderer

from common.utilities import Utilities
from pathlib import Path
from definitions import ROOT_DIR


class RecordTargetTest(unittest.TestCase):

    renderer = Renderer()
    templatePath = Path(ROOT_DIR) / "Partials/RecordTestTemplate.mustache"

    def test_SimpleInput(self):
        input_hash = {
            'recordTarget': {
                'Patient': {
                    'Id': {
                        'root': '2.16.840.1.113883.2.1.4.1',
                        'extension': '9900004948'
                    }
                }
            }
        }

        expected = """
            <recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                </patient>
            </recordTarget>
        """

        render = self.renderer.render_path(self.templatePath, input_hash)
        Utilities.assert_xml_equal(expected, render)

    def test_realmCode(self):
        input_hash = {
            'recordTarget': {
                'Patient': {
                   'Id': {
                        'root': '2.16.840.1.113883.2.1.4.1',
                        'extension': '9900004948'
                    }
                },
                'InfrastructureRootElements': [
                    {'realmCode': [
                        {'realmCode': 'qweqweqwe'}
                    ]}
                ]
            }
        }

        expected = """
            <recordTarget typeCode="RCT" >
                <patient classCode="PAT">
                    <realmCode value="qweqweqwe"/>
                    <id root="2.16.840.1.113883.2.1.4.1" extension="9900004948"/>
                </patient>
            </recordTarget>
        """

        render = self.renderer.render_path(self.templatePath, input_hash)
        
        Utilities.assert_xml_equal(expected, render)

    def test_multiRealmCode(self):
        input_hash = {
            'recordTarget': {
                'Patient': {
                    'Id': {
                        'root': '2.16.840.1.113883.2.1.4.1',
                        'extension': '9900004948'
                    }
                },
                'InfrastructureRootElements': [
                    {'realmCode': [
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

        render = self.renderer.render_path(self.templatePath, input_hash)
        
        Utilities.assert_xml_equal(expected, render)

    def test_typeId(self):
        input_hash = {
            'recordTarget': {
                'Patient': {
                    'Id': {
                        'root': '2.16.840.1.113883.2.1.4.1',
                        'extension': '9900004948'
                    }
                },
                'InfrastructureRootElements': [
                    {'typeId': [
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

        render = self.renderer.render_path(self.templatePath, input_hash)
        
        Utilities.assert_xml_equal(expected, render)

    def test_templateId(self):
        input_hash = {
            'recordTarget': {
                'Patient': {
                    'Id': {
                        'root': '2.16.840.1.113883.2.1.4.1',
                        'extension': '9900004948'
                    }
                },
                'InfrastructureRootElements': [
                    {'templateId': [
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

        render = self.renderer.render_path(self.templatePath, input_hash)
        
        Utilities.assert_xml_equal(expected, render)

    def test_multiTemplateId(self):
        input_hash = {
            'recordTarget': {
                'Patient': {
                    'Id': {
                        'root': '2.16.840.1.113883.2.1.4.1',
                        'extension': '9900004948'
                    }
                },
                'InfrastructureRootElements': [
                    {'templateId': [
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

        render = self.renderer.render_path(self.templatePath, input_hash)
        
        Utilities.assert_xml_equal(expected, render)

    def test_allInfrastructureRootElements(self):
        input_hash = {
            'recordTarget': {
                'Patient': {
                    'Id': {
                        'root': '2.16.840.1.113883.2.1.4.1',
                        'extension': '9900004948'
                    }
                },
                'InfrastructureRootElements': [
                    {'realmCode': [{'realmCode': '1.20222.2012.123'}]},
                    {'typeId': [{'typeId': '1.20222.2012.123'}]},
                    {'templateId': [{'templateId': '1.20222.2012.123'}]}
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

        render = self.renderer.render_path(self.templatePath, input_hash)
        
        Utilities.assert_xml_equal(expected, render)

    def test_multiAllInfrastructureRootElements(self):
        input_hash = {
            'recordTarget': {
                'Patient': {
                    'Id': {
                        'root': '2.16.840.1.113883.2.1.4.1',
                        'extension': '9900004948'
                    }
                },
                'InfrastructureRootElements': [
                    {'realmCode': [{'realmCode': 'realm001'}, {'realmCode': 'realm002'}]},
                    {'typeId': [{'typeId': '1.20222.2012.123'}]},
                    {'templateId': [{'templateId': 'template001'}, {'templateId': 'template002'}]}
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

        render = self.renderer.render_path(self.templatePath, input_hash)

        print(render)
        Utilities.assert_xml_equal(expected, render)
