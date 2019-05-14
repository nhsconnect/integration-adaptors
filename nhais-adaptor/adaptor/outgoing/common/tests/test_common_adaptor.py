import unittest

from fhirclient.models.address import Address as FhirAddress
from fhirclient.models.humanname import HumanName as FhirName
from testfixtures import compare

import adaptor.outgoing.common.common_adaptor as adaptor
from edifact.outgoing.models.address import Address as EdifactAddress
from edifact.outgoing.models.name import Name as EdifactName


class TestCommonAdaptor(unittest.TestCase):
    def test_generate_recipient_from(self):
        """
        Test the generation of a recipient cypher from the nhais cypher
        """
        with self.subTest("When the nhais cypher is 3 characters"):
            recipient_cypher = adaptor.generate_recipient_from('XX1')

            self.assertEqual(recipient_cypher, "XX11")

        with self.subTest("When the nhais cypher is 2 characters"):
            recipient_cypher = adaptor.generate_recipient_from('XX')

            self.assertEqual(recipient_cypher, "XX01")

    def test_create_patient_name(self):
        """ Test the creation of af edifact patient name object from fhir """
        with self.subTest("Patient with all the name details"):
            expected = EdifactName(title="Mr", family_name="Parker", first_given_forename="Peter", middle_name="Spidey",
                                   third_given_forename="Senses")

            name = FhirName({'prefix': ['Mr'], 'family': 'Parker', 'given': ['Peter', 'Spidey', 'Senses']})
            edi_name = adaptor.create_patient_name(name)

            compare(edi_name, expected)

        with self.subTest("Patient with just title, first name and surname"):
            expected = EdifactName(title="Mr", family_name="Parker", first_given_forename="Peter")

            name = FhirName({'prefix': ['Mr'], 'family': 'Parker', 'given': ['Peter']})
            edi_name = adaptor.create_patient_name(name)

            compare(edi_name, expected)

    def test_create_patient_address(self):
        """ Test test creation of an edifact patient address object from fhir """

        with self.subTest("Patient will all address attributes"):
            expected = EdifactAddress(house_name="Spidey House", address_line_1="Spidey Way",
                                      address_line_2="Spiderville", town="Spidey Town", county="Spideyshire",
                                      post_code="SP1 1AA")

            pat_address = FhirAddress(
                {'line': ['Spidey House', 'Spidey Way', 'Spiderville'], 'city': 'Spidey Town',
                 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            edi_address = adaptor.create_patient_address(pat_address)

            compare(edi_address, expected)

        with self.subTest("Patient address without house name"):
            expected = EdifactAddress(address_line_1="1 Spidey Way", address_line_2="Spiderville", town="Spidey Town",
                                      county="Spideyshire", post_code="SP1 1AA")

            pat_address = FhirAddress(
                {'line': ['1 Spidey Way', 'Spiderville'], 'city': 'Spidey Town',
                 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            edi_address = adaptor.create_patient_address(pat_address)

            compare(edi_address, expected)

        with self.subTest("Patient with only 1 address line"):
            expected = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", county="Spideyshire",
                                      post_code="SP1 1AA")
            pat_address = FhirAddress(
                {'line': ['1 Spidey Way'], 'city': 'Spidey Town', 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            edi_address = adaptor.create_patient_address(pat_address)

            compare(edi_address, expected)

        with self.subTest("Patient with only 1 address line and no county details"):
            expected = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")

            pat_address = FhirAddress(
                {'line': ['1 Spidey Way'], 'city': 'Spidey Town', 'postalCode': 'SP1 1AA'})
            edi_address = adaptor.create_patient_address(pat_address)

            compare(edi_address, expected)

    def test_determine_address_lines(self):
        """ Test the determine address line function """

        with self.subTest("When 3 address lines are provided in the fhir patient address"):
            expected = ["house name", "address line 1", "address line 2"]

            fhir_address_with_3_lines = ["house name", "address line 1", "address line 2"]
            generated_address_lines = adaptor.determine_address_lines(fhir_address_with_3_lines)

            compare(generated_address_lines, expected)

        with self.subTest("When 2 address lines are provided in the fhir patient address"):
            expected = ["", "address line 1", "address line 2"]

            fhir_address_with_2_lines = ["address line 1", "address line 2"]
            generated_address_lines = adaptor.determine_address_lines(fhir_address_with_2_lines)

            compare(generated_address_lines, expected)

        with self.subTest("When 1 address line is provided in the fhir patient address"):
            expected = ["", "address line 1", ""]

            fhir_address_with_1_line = ["address line 1"]
            generated_address_lines = adaptor.determine_address_lines(fhir_address_with_1_line)

            compare(generated_address_lines, expected)
