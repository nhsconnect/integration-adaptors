from unittest import TestCase

from integration_tests.helpers import methods


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796
    def test_scr_happy_path(self):
        mhs_response = methods.get_interaction_from_template('QUPC_IN160101UK05',
                                                             'QUPC_IN160101UK05',
                                                             '9689177869',
                                                             'Happy path test')
        self.assertTrue(methods.check_response(mhs_response), "Happy path test failed")
        #print(mhs_response)

    def test_scr_passing_in_message_id(self):
        mhs_response = methods.get_interaction_from_template('gp_summary_upload',
                                                             'REPC_IN150016UK05',
                                                             '9689177869',
                                                             'test with message id',
                                                             pass_message_id=True)
        self.assertTrue(methods.check_response(mhs_response),
                        "Happy path test with message id passed to MHS failed")
