import os
import unittest
from pathlib import Path

from utilities.file_utilities import FileUtilities

from adaptor.outgoing.config import operation_dict
from adaptor.outgoing.outgoing_adaptor import OutgoingAdaptor


class TestOutgoingAdaptor(unittest.TestCase):
    """
    Test that when fhir json payload is loaded the correct edifact message is created
    """

    def test_convert_to_edifact(self):
        """
        Test when the operation is for a birth registration
        """
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))

        expected_file_path = Path(TEST_DIR) / "edifact.txt"
        expected_edifact_interchange = FileUtilities.get_file_string(expected_file_path)

        incoming_file_path = Path(TEST_DIR) / "patient-register-birth.json"
        patient_register_json = FileUtilities.get_file_dict(incoming_file_path)

        outgoing_adaptor = OutgoingAdaptor(operation_dict)
        (sender, recipient, interchange_seq_no, edifact_interchange) = outgoing_adaptor.convert_to_edifact(
            patient_register_json)

        pretty_edifact_interchange = "'\n".join(edifact_interchange.split("'"))
        self.assertEqual(pretty_edifact_interchange, expected_edifact_interchange)
