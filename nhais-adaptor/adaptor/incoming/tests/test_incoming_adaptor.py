import os
import unittest
from pathlib import Path

from testfixtures import compare
from utilities.file_utilities import FileUtilities

from adaptor.incoming.config import reference_dict
from adaptor.incoming.incoming_adaptor import IncomingAdaptor


class TestIncomingAdaptor(unittest.TestCase):
    """
    Test that when fhir json payload is loaded the correct edifact message is created
    """

    def test_covert_to_fhir(self):
        """
        Test when the operation is for a birth registration
        """
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))

        expected_file_path = Path(TEST_DIR) / "patient-register-birth-approval.json"
        patient_register_approval_json = FileUtilities.get_file_dict(expected_file_path)

        incoming_file_path = Path(TEST_DIR) / "edifact.txt"
        incoming_interchange_raw = FileUtilities.get_file_string(incoming_file_path)

        incoming_adaptor = IncomingAdaptor(reference_dict)
        op_defs = incoming_adaptor.covert_to_fhir(incoming_interchange_raw)

        op_def_to_compare = op_defs[0][2]
        compare(op_def_to_compare, patient_register_approval_json)
