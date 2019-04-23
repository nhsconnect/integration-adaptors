import unittest
from pystache import Renderer
from common.utilities import Utilities
from pathlib import Path
from definitions import ROOT_DIR


class ReplacementOfTest(unittest.TestCase):
    renderer = Renderer()
    # TODO:
    #   * Shift these template files to a new folder, the partial broke last time you tried this
    templatePath = "../spike_partials/ReplacementOfTemplate.mustache"
    templatePath = Path(ROOT_DIR) / "spike_partials/ReplacementOfTemplate.mustache"

    def test_basicReplacementOf(self):
        hash = {
            'replacementOf': {
                'priorMessageRef': {
                    'id': {
                        'root': "A05B9416-F700-48F1-99D8-98874D3406B9"
                    }
                }
            }
        }

        expected = """
            <replacementOf typeCode="RPLC">
                <priorMessageRef classCode="COMPOSITION" moodCode="EVN">
                    <id root="A05B9416-F700-48F1-99D8-98874D3406B9"/>
                </priorMessageRef>
            </replacementOf>
        """

        render = self.renderer.render_path(self.templatePath, hash)
        Utilities.assert_xml_equal(expected, render)

    def test_emptyReplacementOf(self):
        hash = {
            'replacementOf': {
                'priorMessageRef': {
                    'id': {}
                }
            }
        }

        expected = """<replacementOf typeCode="RPLC">
                <priorMessageRef classCode="COMPOSITION" moodCode="EVN">
                    <id root=""/>
                </priorMessageRef>
            </replacementOf>
        """

        render = self.renderer.render_path(self.templatePath, hash)
        Utilities.assert_xml_equal(expected, render)

    def test_ReplacementOfWithInfrastructureRootElements(self):
        hash = {
            'replacementOf': {
                'priorMessageRef': {
                    'id': {}
                },
                'InfrastructureRootElements': [
                    { 'realmCode': [{'realmCode': 'realm001'}, {'realmCode': 'realm002'} ]},
                    { 'typeId': [{'typeId': '1.20222.2012.123'}]},
                    { 'templateId': [{'templateId': 'template001'}, {'templateId': 'template002'}]}
                ]
            }
        }

        expected = """
            <replacementOf typeCode="RPLC">
                <realmCode value="realm001"/>
                <realmCode value="realm002"/>
                <typeId value="1.20222.2012.123"/>
                <templateId value="template001"/>
                <templateId value="template002"/>
                <priorMessageRef classCode="COMPOSITION" moodCode="EVN">
                    <id root=""/>
                </priorMessageRef>
            </replacementOf>
        """

        render = self.renderer.render_path(self.templatePath, hash)
        Utilities.assert_xml_equal(expected, render)
