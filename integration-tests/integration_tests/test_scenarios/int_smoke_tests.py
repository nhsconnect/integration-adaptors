from unittest import skip, TestCase
from integration_tests.helpers import methods, interactions, message_retriever, xml_parser


class FunctionalTest(TestCase):

    # Message Pattern Type: Forward Reliable
    # Interaction: GP2GP Common Content Large Messaging (COPC_IN000001UK01)
    @skip('waiting for RT-14 - Implement MHS Forward Reliable Message Pattern')
    def test_mhs_forward_reliable(self):
        mhs_response, _, _ = methods.get_interaction_from_template('forward_reliable',
                                                                   'COPC_IN000001UK01',
                                                                   '9446245796',
                                                                   'Forward Reliable test')
        self.assertTrue(methods.check_response(mhs_response, 'requestSuccessDetail'),
                        "Forward Reliable smoke test failed")

