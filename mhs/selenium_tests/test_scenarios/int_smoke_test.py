
from unittest import TestCase
from selenium_tests.page_objects import methods


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796
    def test_scr_happy_path(self):
        interaction_name = 'gp_summary_upload'
        nhs_number = '9446245796'

        self.assertTrue(methods.check_scr_response(
            methods.get_interaction(interaction_name, nhs_number)), "Happy path test failed")
