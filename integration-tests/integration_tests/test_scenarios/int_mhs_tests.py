from unittest import TestCase

from integration_tests.helpers import methods

SUMMARY_UPLOAD_INTERACTION = 'gp_summary_upload'
TEST_NHS_NUMBER = '9446245796'


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796
    def test_scr_happy_path(self):
        mhs_response = methods.get_interaction_from_template(SUMMARY_UPLOAD_INTERACTION,
                                                             'xml_REPC_IN150016UK05',
                                                             TEST_NHS_NUMBER)
        self.assertTrue(methods.check_response(mhs_response), "Happy path test failed")

    def test_scr_passing_in_message_id(self):
        mhs_response = methods.get_interaction_from_template(SUMMARY_UPLOAD_INTERACTION,
                                                             'xml_REPC_IN150016UK05',
                                                             TEST_NHS_NUMBER,
                                                             pass_message_id=True)
        self.assertTrue(methods.check_response(mhs_response),
                        "Happy path test with message id passed to MHS failed")
