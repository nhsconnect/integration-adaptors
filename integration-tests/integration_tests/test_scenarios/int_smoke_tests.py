from unittest import skip, TestCase

from integration_tests.helpers import methods, interactions


class FunctionalTest(TestCase):

    # Message Pattern Type: Asynchronous Express
    # Interaction: PSIS Document List Data Request (QUPC_IN160101UK05)
    def test_mhs_async_express(self):
        mhs_response = methods.get_interaction_from_template('QUPC_IN160101UK05',
                                                             '9689174746',
                                                             'Asynchronous Express test')
        self.assertTrue(methods.check_response(mhs_response), "Asynchronous Express test failed")

    def test_mhs_async_express_with_message_id(self):
        mhs_response = methods.get_interaction_from_template('QUPC_IN160101UK05',
                                                             '9689174746',
                                                             'Asynchronous Express test',
                                                             pass_message_id=True)
        self.assertTrue(methods.check_response(mhs_response), "Asynchronous Express test with message id failed")


    # Message Pattern Type: Asynchronous Reliable
    # Interaction: GP Summary (REPC_IN150016UK05)
    @skip('waiting for RT-12 - Implement MHS Async Reliable Message Pattern')
    def test_mhs_async_reliable(self):
        mhs_response = methods.get_interaction_from_template('REPC_IN150016UK05',
                                                             '9446245796',
                                                             'Asynchronous Reliable test')
        self.assertTrue(methods.check_response(mhs_response), "Asynchronous Reliable test failed")

    @skip('waiting for RT-12 - Implement MHS Async Reliable Message Pattern')
    def test_mhs_async_reliable_with_message_id(self):
        mhs_response = methods.get_interaction_from_template('REPC_IN150016UK05',
                                                             '9446245796',
                                                             'Asynchronous Reliable test',
                                                             pass_message_id=True)
        self.assertTrue(methods.check_response(mhs_response), "Asynchronous Reliable test with message id failed")


    # Message Pattern Type: Synchronous
    # Interaction: PDS Retrieval Query (QUPA_IN040000UK32)
    @skip('waiting for RT-15 - Implement MHS Synchronous Message Pattern')
    def test_mhs_synchronous(self):
        mhs_response = methods.get_interaction_from_template('QUPA_IN040000UK32',
                                                             '9689174606',
                                                             'Synchronous test')
        self.assertTrue(methods.check_response(mhs_response), "Synchronous test failed")

    @skip('waiting for RT-15 - Implement MHS Synchronous Message Pattern')
    def test_mhs_synchronous_with_message_id(self):
        mhs_response = methods.get_interaction_from_template('QUPA_IN040000UK32',
                                                             '9689174606',
                                                             'Synchronous test',
                                                             pass_message_id=True)
        self.assertTrue(methods.check_response(mhs_response), "Synchronous test with message id failed")


    # Message Pattern Type: Forward Reliable
    # Interaction: GP2GP Common Content Large Messaging (COPC_IN000001UK01)
    @skip('waiting for RT-14 - Implement MHS Forward Reliable Message Pattern')
    def test_mhs_forward_reliable(self):
        mhs_response = methods.get_interaction_from_template('COPC_IN000001UK01',
                                                             '9446245796',
                                                             'Forward Reliable test')
        self.assertTrue(methods.check_response(mhs_response), "Forward Reliable test failed")

    @skip('waiting for RT-14 - Implement MHS Forward Reliable Message Pattern')
    def test_mhs_forward_reliable_with_message_id(self):
        mhs_response = methods.get_interaction_from_template('COPC_IN000001UK01',
                                                             '9446245796',
                                                             'Forward Reliable test',
                                                             pass_message_id=True)
        self.assertTrue(methods.check_response(mhs_response), "Forward Reliable test with message id failed")


    # Message Pattern Type: Asynchronous Reliable
    # Interaction: SCR-Adaptor using json template (json_hash16UK05), which forms GP Summary (REPC_IN150016UK05)
    @skip('waiting for RT-12 - Implement MHS Async Reliable Message Pattern')
    def test_scr_adaptor(self):
        scr_json, uuid = methods.get_json('hash16UK05', 9689177869, 'json message test')

        # send this to the adaptor to 'convert' it to HL7
        scr_response = interactions.call_scr_adaptor(scr_json)

        # now send the scr_response to the mhs
        mhs_response = interactions.call_mhs('REPC_IN150016UK05', scr_response)

        # then validate the mhs-response
        self.assertTrue(methods.check_response(mhs_response), "Unsuccessful response from Spine")
