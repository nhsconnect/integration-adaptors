
from unittest import TestCase

from integration_tests.helpers import methods


SUMMARY_UPLOAD_INTERACTION = 'gp_summary_upload'
TEMPLATE_JSON = 'json_hash16UK05'
TEST_NHS_NUMBER = '9446245796'


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796
    def test_json_conversion(self):
        scr_json, uuid = methods.get_json(TEMPLATE_JSON, TEST_NHS_NUMBER)

        # send this to the adaptor to 'convert' it to HL7
        scr_response = methods.call_scr_adaptor(scr_json)

        # now send the scr_response to the mhs
        mhs_response = methods.get_interaction_from_message(SUMMARY_UPLOAD_INTERACTION, scr_response)

        # then validate the mhs-response
        self.assertTrue(methods.check_response(mhs_response), "Unsuccessful response from Spine")
