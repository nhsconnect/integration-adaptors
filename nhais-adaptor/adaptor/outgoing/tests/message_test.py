import unittest
from testfixtures import compare
from adaptor.outgoing.message import MessageAdaptor
from fhirclient.models.patient import Patient
from fhirclient.models.humanname import HumanName
from fhirclient.models.identifier import Identifier
from fhirclient.models.address import Address
from edifact.models.name import Name
from edifact.models.address import Address as EdifactAddress
from edifact.models.message import MessageSegmentPatientDetails


class MessageAdaptorTest(unittest.TestCase):
    """
    Tests the conversion of fhir to edifact
    """

    def test_create_patient_name(self):
        """ Test the creation of af edifact patient name object from fhir """
        with self.subTest("Patient with all the name details"):
            name = HumanName({'prefix': ['Mr'], 'family': 'Parker', 'given': ['Peter', 'Spidey', 'Senses']})
            expected = Name(title="Mr", family_name="Parker", first_given_forename="Peter", middle_name="Spidey",
                            third_given_forename="Senses")
            edi_name = MessageAdaptor.create_patient_name(name)
            compare(edi_name, expected)

        with self.subTest("Patient with just title, first name and surname"):
            name = HumanName({'prefix': ['Mr'], 'family': 'Parker', 'given': ['Peter']})
            expected = Name(title="Mr", family_name="Parker", first_given_forename="Peter")
            edi_name = MessageAdaptor.create_patient_name(name)
            compare(edi_name, expected)

    def test_create_patient_address(self):
        """ Test test creation of an edifact patient address object from fhir """

        with self.subTest("Patient will all address attributes"):
            pat_address = Address(
                {'line': ['Spidey House', 'Spidey Way', 'Spiderville'], 'city': 'Spidey Town',
                 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            expected = EdifactAddress(house_name="Spidey House", address_line_1="Spidey Way",
                                      address_line_2="Spiderville", town="Spidey Town", county="Spideyshire",
                                      post_code="SP1 1AA")
            edi_address = MessageAdaptor.create_patient_address(pat_address)
            compare(edi_address, expected)

        with self.subTest("Patient address without house name"):
            pat_address = Address(
                {'line': ['1 Spidey Way', 'Spiderville'], 'city': 'Spidey Town',
                 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            expected = EdifactAddress(address_line_1="1 Spidey Way", address_line_2="Spiderville", town="Spidey Town",
                                      county="Spideyshire", post_code="SP1 1AA")
            edi_address = MessageAdaptor.create_patient_address(pat_address)
            compare(edi_address, expected)

        with self.subTest("Patient with only 1 address line"):
            pat_address = Address(
                {'line': ['1 Spidey Way'], 'city': 'Spidey Town', 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            expected = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", county="Spideyshire",
                                      post_code="SP1 1AA")
            edi_address = MessageAdaptor.create_patient_address(pat_address)
            compare(edi_address, expected)

        with self.subTest("Patient with only 1 address line and no county details"):
            pat_address = Address(
                {'line': ['1 Spidey Way'], 'city': 'Spidey Town', 'postalCode': 'SP1 1AA'})
            expected = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            edi_address = MessageAdaptor.create_patient_address(pat_address)
            compare(edi_address, expected)

    def test_create_message_segment_patient_details(self):
        """
        Test the function to create an edifact message segment for patient details
        """

        with self.subTest("Patient with no previous names or addresses"):
            pat_address = Address({'line': ['1 Spidey Way'], 'city': 'Spidey Town', 'postalCode': 'SP1 1AA'})
            nhs_number = Identifier({'value': 'NHSNO11111'})
            name = HumanName({'prefix': ['Mr'], 'family': 'Parker', 'given': ['Peter']})
            patient = Patient({'identifier': [nhs_number.as_json()], 'gender': 'male', 'name': [name.as_json()],
                               'birthDate': '2019-04-23', 'address': [pat_address.as_json()]})

            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            expected = MessageSegmentPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                    date_of_birth="2019-04-23",
                                                    gender="1", address=edifact_pat_address)

            msg_seg_pat_details = MessageAdaptor.create_message_segment_patient_detail(patient)

            compare(msg_seg_pat_details, expected)
