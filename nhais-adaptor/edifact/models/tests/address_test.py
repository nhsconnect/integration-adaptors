import unittest
from edifact.models.address import PatientAddress, Address


class PatientAddressTest(unittest.TestCase):
    """
    Test the generating of the patient address segment
    """

    def test_patient_address_to_edifact(self):
        with self.subTest("When all the address attributes are provided"):
            expected_edifact_message = "NAD+PAT++MOORSIDE FARM:OLD LANE:ST PAULS CRAY:ORPINGTON:KENT+++++BR6 7EW'"
            address = Address(house_name="MOORSIDE FARM", address_line_1="OLD LANE", address_line_2="ST PAULS CRAY",
                              town="ORPINGTON", county="KENT", post_code="BR6 7EW")
            pat_address_segment = PatientAddress(address=address).to_edifact()
            self.assertEqual(expected_edifact_message, pat_address_segment)

        with self.subTest("When the house name is not provided"):
            expected_edifact_message = "NAD+PAT++:5 OLD LANE:ST PAULS CRAY:ORPINGTON:KENT+++++BR6 7EW'"
            address = Address(address_line_1="5 OLD LANE", address_line_2="ST PAULS CRAY", town="ORPINGTON",
                              county="KENT", post_code="BR6 7EW")
            pat_address_segment = PatientAddress(address=address).to_edifact()
            self.assertEqual(expected_edifact_message, pat_address_segment)

        with self.subTest("When the house name, address line and county are not provided"):
            expected_edifact_message = "NAD+PAT++:5 OLD LANE::ORPINGTON:+++++BR6 7EW'"
            address = Address(address_line_1="5 OLD LANE", town="ORPINGTON", post_code="BR6 7EW")
            pat_address_segment = PatientAddress(address=address).to_edifact()
            self.assertEqual(expected_edifact_message, pat_address_segment)

