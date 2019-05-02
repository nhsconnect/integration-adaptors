import unittest
from pathlib import Path

from utilities.file_utilities import FileUtilities
from utilities.xml_utilities import XmlUtilities
from OneOneOne.OneOneOne.message_handler import MessageHandler

from definitions import ROOT_DIR


class MessageHandlerTest(unittest.TestCase):

    xmlFileDir = Path(ROOT_DIR) / 'OneOneOne' / 'tests' / 'expected_output_xmls'
    hashFileDir = Path(ROOT_DIR + '/scr/tests/hashes/')
    action_does_not_match_service = """
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing"
                   xmlns:itk="urn:nhs-itk:ns:201005">
        <soap:Header>
            <wsa:Action>urn:nhs-itk:services:201005:SendNHS111Report-v2-0</wsa:Action>
        </soap:Header>
        <soap:Body>
            <itk:DistributionEnvelope
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <itk:header service="urn:nhs-itk:services:201005:SendNHS111Report-v2-0_Bad_Service"
                            trackingid="7D6F23E0-AE1A-11DB-9808-B18E1E0994CD">        
                </itk:header>
            </itk:DistributionEnvelope>
        </soap:Body>
    </soap:Envelope>
    """

    def test_action_not_matching_service(self):
        mh = MessageHandler(self.action_does_not_match_service)
        status_code, response = mh.evaluate_message()

        assert(status_code == 500)

        expected = FileUtilities.get_file_string(str(self.xmlFileDir / 'invalid_action_service_values_response.xml'))

        XmlUtilities.assert_xml_equal_utf_8(expected, response)
