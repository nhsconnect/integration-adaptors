
from unittest import TestCase

from integration_tests.helpers import interactions, methods

# SUMMARY_UPLOAD_INTERACTION = 'gp_summary_upload'
# TEMPLATE_JSON = 'hash16UK05'
# TEST_NHS_NUMBER = '9446245796'


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796, using json template (json_hash16UK05)
    def test_json_conversion(self):
        scr_json, uuid = methods.get_json('hash16UK05', 9446245796, 'json message test')

        # send this to the adaptor to 'convert' it to HL7
        scr_response = interactions.call_scr_adaptor(scr_json)

        # now send the scr_response to the mhs
        mhs_response = interactions.call_mhs('gp_summary_upload', scr_response)

        # then validate the mhs-response
        self.assertTrue(methods.check_response(mhs_response), "Unsuccessful response from Spine")
