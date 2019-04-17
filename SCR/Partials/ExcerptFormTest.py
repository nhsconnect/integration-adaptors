
import unittest
from pystache import Renderer
from XmlHelper import XmlHelper

class ExcerptFormTest(unittest.TestCase):
    renderer = Renderer()
    templatePath = "ExcerptFormTemplate.mustache"
    time = "200703151600"

    def test_basicExerptForm(self):
        hash = {
            'excerptForm': {
                'CareProfessionalDocumentationCRE': {
                    'presentationText': {
                        'value': '<h1>hello</h1>',
                        'id': "qweqwewqe",
                        'effectiveTime': "200703151600"
                    }
                }
            }
        }

        expected = """
                <excerptFrom typeCode="XCRPT" contextConductionInd="true" inversionInd="false" negationInd="false">
    <templateId root="2.16.840.1.113883.2.1.3.2.4.18.2" extension="CSAT_RM-NPfITUK10.excerptFrom"/>
    <seperatableInd value="false"/>
    <UKCT_MT144051UK01.CareProfessionalDocumentationCRE classCode="CATEGORY" moodCode="EVN">
        <code codeSystem="2.16.840.1.113883.2.1.3.2.4.15" code="163171000000105" displayName="Care Professional Documentation"/>
        <component typeCode="COMP" inversionInd="false" negationInd="false">
            <templateId root="2.16.840.1.113883.2.1.3.2.4.18.2" extension="CSAB_RM-NPfITUK10.component"/>
            <seperatableInd value="false"/>
            <presentationText classCode="OBS" moodCode="EVN">
                <value mediaType="text/plain" xsi:type="ED.NPfIT.Text.XHTML">
                    <html xmlns="xhtml:NPfIT:PresentationText">
                        <h1>hello</h1>
                    </html>
                </value>
                <id root="qweqwewqe"/>
                <code codeSystem="2.16.840.1.113883.2.1.3.2.4.17.126" code="PresentationText" displayName="Presentation Text"/>
                <statusCode code="completed"/>
                <effectiveTime value="200703151600"/>
            </presentationText>
        </component>
    </UKCT_MT144051UK01.CareProfessionalDocumentationCRE>
</excerptFrom>
        """

        render = self.renderer.render_path(self.templatePath, hash)
        XmlHelper.assertXmlStringsEqual(expected, render)