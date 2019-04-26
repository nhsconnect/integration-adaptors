import unittest
from edifact.models.name import PatientName, Name


class PatientNameTest(unittest.TestCase):
    """
    Test the generating of the patient name segment
    """

    def test_patient_name_to_edifact(self):

        with self.subTest("When all the name attributes are provided"):
            expected_edifact_message = "PNA+PAT+N/10/10:OPI+++SU:STEVENS+FO:CHARLES+TI:MR+MI:ANTHONY+FS:JOHN'"
            name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr", middle_name="Anthony",
                            third_given_forename="John")
            pat_name_segment = PatientName(id_number="N/10/10", name=name).to_edifact()
            self.assertEqual(expected_edifact_message, pat_name_segment)

        with self.subTest("When middle name and third given forename is not provided"):
            expected_edifact_message = "PNA+PAT+N/10/10:OPI+++SU:STEVENS+FO:CHARLES+TI:MR'"
            name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr")
            pat_name_segment = PatientName(id_number="N/10/10", name=name).to_edifact()
            self.assertEqual(expected_edifact_message, pat_name_segment)

        with self.subTest("When third given forename is not provided"):
            expected_edifact_message = "PNA+PAT+N/10/10:OPI+++SU:STEVENS+FO:CHARLES+TI:MR+MI:ANTHONY'"
            name = Name(family_name="Stevens", first_given_forename="Charles", title="Mr", middle_name="Anthony")
            pat_name_segment = PatientName(id_number="N/10/10", name=name).to_edifact()
            self.assertEqual(expected_edifact_message, pat_name_segment)

