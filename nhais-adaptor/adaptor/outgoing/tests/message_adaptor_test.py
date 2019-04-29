import unittest
from testfixtures import compare
from adaptor.outgoing.message_adaptor import MessageAdaptor
from adaptor.outgoing.fhir_helpers.operation_definition import OperationDefinitionHelper as odh
from adaptor.outgoing.fhir_helpers.tests.fixtures import Fixtures
from fhirclient.models.humanname import HumanName
from fhirclient.models.address import Address
from edifact.models.name import Name
from edifact.models.address import Address as EdifactAddress
from edifact.models.message import MessageSegmentPatientDetails, MessageSegmentRegistrationDetails, MessageBeginning


class MessageAdaptorPatientDetailsTest(unittest.TestCase):
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
        Test the function to create an edifact segment for patient details
        """

        with self.subTest("Patient with no previous names or addresses"):
            patient = Fixtures.create_simple_patient()

            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            expected = MessageSegmentPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                    date_of_birth="2019-04-23",
                                                    gender="1", address=edifact_pat_address)

            msg_seg_pat_details = MessageAdaptor.create_message_segment_patient_detail(patient)

            compare(msg_seg_pat_details, expected)

    def test_create_message_segment_registration_details(self):
        """
        Test the function to create an edifact segment for the registration details
        """

        with self.subTest("Patient registration details for type birth"):
            op_param_transaction_number = odh.create_parameter_with_binding(name="transactionNumber", value="17")

            practitioner = odh.create_practitioner_resource(resource_id="practitioner-1", national_identifier="4826940",
                                                            local_identifier="281")

            patient = Fixtures.create_simple_patient()

            op_param_practitioner = odh.create_parameter_with_resource_ref(name="registerPractitioner",
                                                                           resource_type="Practitioner",
                                                                           reference="practitioner-1")

            op_param_patient = odh.create_parameter_with_resource_ref(name="registerPatient", resource_type="Patient",
                                                                      reference="patient-1")

            op_def = odh.create_operation_definition(name="RegisterPatient-Birth",
                                                     code="gpc.registerpatient",
                                                     date_time="2019-04-23 09:00:04.159338",
                                                     contained=[practitioner, patient],
                                                     parameter=[op_param_transaction_number,
                                                                op_param_practitioner, op_param_patient])

            expected = MessageSegmentRegistrationDetails(transaction_number=17,
                                                         party_id="4826940,281",
                                                         acceptance_code="A",
                                                         acceptance_type=1,
                                                         date_time="2019-04-23 09:00:04.159338",
                                                         location="Spidey Town")

            msg_seg_reg_details = MessageAdaptor.create_message_segment_registration_details(op_def)

            compare(msg_seg_reg_details, expected)

    def test_create_message_beginning(self):
        """
        Test the function to create an edifact section representing the beginning of a message
        """
        with self.subTest("Message beginning for a birth registration"):
            op_param_nhais_id = odh.create_parameter_with_binding(name="nhaisCypher", value="XX1")

            op_def = odh.create_operation_definition(name="RegisterPatient-Birth",
                                                     code="gpc.registerpatient",
                                                     date_time="2019-04-23 09:00:04.159338",
                                                     contained=[],
                                                     parameter=[op_param_nhais_id])
            expected = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")

            msg_bgn = MessageAdaptor.create_message_beginning(fhir_operation=op_def)

            compare(msg_bgn, expected)


