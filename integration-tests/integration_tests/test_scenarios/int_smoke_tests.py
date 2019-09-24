from unittest import skip, TestCase
from integration_tests.helpers import methods, interactions, message_retriever, xml_parser


class FunctionalTest(TestCase):

    # Message Pattern Type: Forward Reliable
    # Interaction: GP2GP Common Content Large Messaging (COPC_IN000001UK01)
    def test_mhs_forward_reliable(self):
        mhs_response, _, _ = methods.get_interaction_from_template('forward_reliable',
                                                                   'COPC_IN000001UK01',
                                                                   '9446245796',
                                                                   'Forward Reliable test')
        self.assertTrue(methods.check_response(mhs_response, 'requestSuccessDetail'),
                        "Forward Reliable smoke test failed")

    # Message Pattern Type: Asynchronous Reliable
    # Interaction: SCR-Adaptor using json template (json_hash16UK05), which forms GP Summary (REPC_IN150016UK05)
    @skip('waiting RT-136 and RT-90')
    def test_scr_adaptor(self):
        scr_json, uuid = methods.get_json('hash16UK05', '9689177869', 'json message test')

        # send this to the adaptor to 'convert' it to HL7
        scr_response = interactions.call_scr_adaptor(scr_json)

        # now send the scr_response to the mhs
        # This may not be necessary, as the adaptor may do this for us..
        mhs_response = interactions.call_mhs('REPC_IN150016UK05', scr_response, None, False, None, False, False)

        # then validate the mhs-response
        self.assertTrue(methods.check_response(mhs_response, 'requestSuccessDetail'),
                        "Unsuccessful response from Spine")
