import os
import unittest
from pathlib import Path

from testfixtures import compare
from utilities.file_utilities import FileUtilities

import adaptor.incoming.operation_definition_adaptor as adaptor
import edifact.incoming.parser.deserialiser as deserialiser


class TestEdifactToFhirIntegration(unittest.TestCase):
    """
    Test that when fhir json payload is loaded the correct edifact message is created
    """

    def test_patient_registration_birth_approval(self):
        """
        Test when the operation is for a birth registration
        """
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))

        expected_file_path = Path(TEST_DIR) / "patient-register-birth-approval.json"
        patient_register_approval_json = FileUtilities.get_file_dict(expected_file_path)

        incoming_file_path = Path(TEST_DIR) / "edifact.txt"
        incoming_interchange_raw = FileUtilities.get_file_string(incoming_file_path)

        lines = incoming_interchange_raw.split("'\n")
        interchange = deserialiser.convert(lines)

        op_defs = adaptor.create_operation_definition(interchange)
        pretty_op_def = op_defs[0][2].as_json()

        compare(pretty_op_def, patient_register_approval_json)
