from unittest import TestCase, skip

from integration_tests.helpers import interactions, methods
from integration_tests.helpers.build_message import build_message
from integration_tests.helpers.methods import get_asid
from integration_tests.http.scr_http_request_builder import ScrHttpRequestBuilder


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796, using json template (json_hash16UK05)
    @skip('waiting for RT-12 - Implement MHS Async Reliable Message Pattern')
    def test_json_conversion(self):
        scr_json, uuid = methods.get_json('hash16UK05', 9689177869, 'json message test')

        # send this to the adaptor to 'convert' it to HL7
        scr_response = interactions.call_scr_adaptor(scr_json)

        # now send the scr_response to the mhs
        mhs_response = interactions.call_mhs('gp_summary_upload', scr_response, None, False, None, False)

        # then validate the mhs-response
        self.assertTrue(methods.check_response(mhs_response, 'requestSuccessDetail'),
                        "Unsuccessful response from Spine")

    def test_should_return_success_response_json(self):
        scr_json, message_id = build_message('json_16UK05', get_asid(), '9689174606', 'Scr GP Summary Upload test')

        response = ScrHttpRequestBuilder() \
            .with_headers(interaction_name='SCR_GP_SUMMARY_UPLOAD',
                          message_id=message_id,
                          correlation_id='2') \
            .with_body(scr_json) \
            .execute_post_expecting_success()

        print(response.text)
