from unittest import TestCase, skip

from selenium_tests.page_objects import methods

TEST_NHS_NUMBER = '9446245796'
GP_SUMMARY_UPLOAD_INTERACTION = 'gp_summary_upload'


@skip("Sync Async workflow not implemented yet")
class SyncAsyncTest(TestCase):

    # request scr record for patient 9446245796
    def test_scr_happy_path(self):
        mhs_response = methods.get_interaction(GP_SUMMARY_UPLOAD_INTERACTION, TEST_NHS_NUMBER)
        self.assertTrue(methods.check_scr_response(mhs_response), "Happy path test failed")

    def test_scr_passing_in_message_id(self):
        mhs_response = methods.get_interaction(GP_SUMMARY_UPLOAD_INTERACTION, TEST_NHS_NUMBER, pass_message_id=True)
        self.assertTrue(methods.check_scr_response(mhs_response),
                        "Happy path test with message id passed to MHS failed")
