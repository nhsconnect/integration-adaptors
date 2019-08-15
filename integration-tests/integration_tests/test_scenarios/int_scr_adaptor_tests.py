from pathlib import Path

from utilities.file_utilities import FileUtilities

from unittest import TestCase

from integration_tests.helpers import methods
from test_definitions import ROOT_DIR

GP_SUMMARY_UPLOAD_INTERACTION = 'gp_summary_upload'
JSON_TEMPLATE = 'json_hash16UK05'
TEST_NHS_NUMBER = '9446245796'


class FunctionalTest(TestCase):

    # request scr record for patient 9446245796
    def test_json_conversion(self):
        scr_json, uuid = methods.get_json(JSON_TEMPLATE, TEST_NHS_NUMBER)

        # send this to the adaptor to 'convert' it to HL7
        scr_response = methods.call_scr_adaptor(scr_json)

        # TODO
        # once we know the mhs end point, we need to send the scr_response to the mhs
        # meanwhile, use this example response...
        mhs_response = FileUtilities.get_file_string(
            str(Path(ROOT_DIR) / 'integration_tests/data/example_mhs_response.xml'))

        # then validate the mhs-response
        self.assertTrue(methods.check_response(mhs_response), "Happy path test failed")
