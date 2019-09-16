from unittest import TestCase, skip

from integration_tests.helpers import interactions, methods


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796, using json template (json_hash16UK05)
    @skip('waiting for RT-12 - Implement MHS Async Reliable Message Pattern')
    def test_json_conversion(self):
        scr_json, uuid = methods.get_json('hash16UK05', 9689177869, 'json message test')

        # send this to the adaptor to 'convert' it to HL7
        scr_response = interactions.call_scr_adaptor(scr_json)

        # now send the scr_response to the mhs
        mhs_response = interactions.call_mhs('gp_summary_upload', scr_response, None, False, None, False, False)

        # then validate the mhs-response
        self.assertTrue(methods.check_response(mhs_response, 'requestSuccessDetail'),
                        "Unsuccessful response from Spine")
