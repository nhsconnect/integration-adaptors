from pathlib import Path

from utilities.file_utilities import FileUtilities
from scr_definitions import ROOT_DIR

from integration_tests.page_objects import methods
from unittest import TestCase

GP_SUMMARY_UPLOAD_INTERACTION = 'gp_summary_upload'
JSON_TEMPLATE = 'json_hash16UK05'
TEST_NHS_NUMBER = '9446245796'


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796
    def test_json_conversion(self):
        scr_json, uuid = methods.get_json(JSON_TEMPLATE, TEST_NHS_NUMBER)

        # send this to the adaptor to 'convert' it to HL7
        scr_response = methods.call_scr_adaptor(scr_json)

        # todo - send this (scr_response) to the mhs and validate what comes back...
        # meanwhile, use this example response...
        mha_response = FileUtilities.get_file_string(
            str(Path(ROOT_DIR) / 'integration_tests/data/example_response.xml'))

        self.assertTrue(methods.check_response(mha_response), "Happy path test failed")
