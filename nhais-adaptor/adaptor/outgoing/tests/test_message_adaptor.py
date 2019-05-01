import unittest
import adaptor.outgoing.tests.fixtures as fixtures
from testfixtures import compare
import adaptor.outgoing.message_adaptor as message_adaptor
import adaptor.outgoing.fhir_helpers.fhir_creators as creators
from adaptor.outgoing.fhir_helpers.fhir_creators import ParameterName, ResourceType, OperationName
from fhirclient.models.humanname import HumanName
from fhirclient.models.address import Address
from edifact.models.name import Name
from edifact.models.address import Address as EdifactAddress
from edifact.models.message import MessageSegmentPatientDetails, MessageSegmentRegistrationDetails, MessageBeginning, \
    Message


class TestMessageAdaptor(unittest.TestCase):
    """
    Tests the conversion of fhir to edifact
    """

    def test_create_patient_name(self):
        """ Test the creation of af edifact patient name object from fhir """
        with self.subTest("Patient with all the name details"):
            expected = Name(title="Mr", family_name="Parker", first_given_forename="Peter", middle_name="Spidey",
                            third_given_forename="Senses")

            name = HumanName({'prefix': ['Mr'], 'family': 'Parker', 'given': ['Peter', 'Spidey', 'Senses']})
            edi_name = message_adaptor.create_patient_name(name)

            compare(edi_name, expected)

        with self.subTest("Patient with just title, first name and surname"):
            expected = Name(title="Mr", family_name="Parker", first_given_forename="Peter")

            name = HumanName({'prefix': ['Mr'], 'family': 'Parker', 'given': ['Peter']})
            edi_name = message_adaptor.create_patient_name(name)

            compare(edi_name, expected)

    def test_create_patient_address(self):
        """ Test test creation of an edifact patient address object from fhir """

        with self.subTest("Patient will all address attributes"):
            expected = EdifactAddress(house_name="Spidey House", address_line_1="Spidey Way",
                                      address_line_2="Spiderville", town="Spidey Town", county="Spideyshire",
                                      post_code="SP1 1AA")

            pat_address = Address(
                {'line': ['Spidey House', 'Spidey Way', 'Spiderville'], 'city': 'Spidey Town',
                 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            edi_address = message_adaptor.create_patient_address(pat_address)

            compare(edi_address, expected)

        with self.subTest("Patient address without house name"):
            expected = EdifactAddress(address_line_1="1 Spidey Way", address_line_2="Spiderville", town="Spidey Town",
                                      county="Spideyshire", post_code="SP1 1AA")

            pat_address = Address(
                {'line': ['1 Spidey Way', 'Spiderville'], 'city': 'Spidey Town',
                 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            edi_address = message_adaptor.create_patient_address(pat_address)

            compare(edi_address, expected)

        with self.subTest("Patient with only 1 address line"):
            expected = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", county="Spideyshire",
                                      post_code="SP1 1AA")
            pat_address = Address(
                {'line': ['1 Spidey Way'], 'city': 'Spidey Town', 'district': 'Spideyshire', 'postalCode': 'SP1 1AA'})
            edi_address = message_adaptor.create_patient_address(pat_address)

            compare(edi_address, expected)

        with self.subTest("Patient with only 1 address line and no county details"):
            expected = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")

            pat_address = Address(
                {'line': ['1 Spidey Way'], 'city': 'Spidey Town', 'postalCode': 'SP1 1AA'})
            edi_address = message_adaptor.create_patient_address(pat_address)

            compare(edi_address, expected)

    def test_create_message_segment_patient_details(self):
        """
        Test the function to create an edifact segment for patient details
        """

        with self.subTest("Patient with no previous names or addresses"):
            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            expected = MessageSegmentPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                    date_of_birth="2019-04-20",
                                                    gender="1", address=edifact_pat_address)

            patient = fixtures.create_simple_patient()
            op_param_patient = creators.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PATIENT,
                                                                           resource_type=ResourceType.PATIENT,
                                                                           reference="patient-1")
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_BIRTH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338", contained=[patient],
                                                          parameters=[op_param_patient])
            msg_seg_pat_details = message_adaptor.create_message_segment_patient_detail(op_def)

            compare(msg_seg_pat_details, expected)

    def test_create_message_segment_registration_details(self):
        """
        Test the function to create an edifact segment for the registration details
        """

        with self.subTest("Patient registration details for type birth"):
            expected = MessageSegmentRegistrationDetails(transaction_number=17,
                                                         party_id="4826940,281",
                                                         acceptance_code="A",
                                                         acceptance_type=1,
                                                         date_time="2019-04-23 09:00:04.159338",
                                                         location="Spidey Town")

            op_param_transaction_number = creators.create_parameter_with_binding(name=ParameterName.TRANSACTION_NO,
                                                                                 value="17")
            practitioner = fixtures.create_simple_practitioner()
            patient = fixtures.create_simple_patient()
            op_param_practitioner = creators.create_parameter_with_resource_ref(
                name=ParameterName.REGISTER_PRACTITIONER,
                resource_type=ResourceType.PRACTITIONER,
                reference="practitioner-1")
            op_param_patient = creators.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PATIENT,
                                                                           resource_type=ResourceType.PATIENT,
                                                                           reference="patient-1")
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_BIRTH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338",
                                                          contained=[practitioner, patient],
                                                          parameters=[op_param_transaction_number,
                                                                      op_param_practitioner, op_param_patient])

            msg_seg_reg_details = message_adaptor.create_message_segment_registration_details(op_def)

            compare(msg_seg_reg_details, expected)

    def test_create_message_beginning(self):
        """
        Test the function to create an edifact section representing the beginning of a message
        """
        with self.subTest("Message beginning for a birth registration"):
            expected = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")

            op_param_nhais_cypher = creators.create_parameter_with_binding(name=ParameterName.NHAIS_CYPHER, value="XX1")
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_BIRTH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338", contained=[],
                                                          parameters=[op_param_nhais_cypher])

            msg_bgn = message_adaptor.create_message_beginning(fhir_operation=op_def)

            compare(msg_bgn, expected)

    def test_create_message(self):
        """
        Test the function to create an edifact message
        """
        with self.subTest("Birth Registration"):
            msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")
            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            msg_seg_pat_details = MessageSegmentPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                               date_of_birth="2019-04-20",
                                                               gender="1", address=edifact_pat_address)
            msg_seg_reg_details = MessageSegmentRegistrationDetails(transaction_number=17,
                                                                    party_id="4826940,281",
                                                                    acceptance_code="A",
                                                                    acceptance_type=1,
                                                                    date_time="2019-04-23 09:00:04.159338",
                                                                    location="Spidey Town")
            expected = Message(sequence_number="000001", message_beginning=msg_bgn,
                               message_segment_registration_details=msg_seg_reg_details,
                               message_segment_patient_details=msg_seg_pat_details)

            op_param_message_sequence = creators.create_parameter_with_binding(name=ParameterName.MESSAGE_SEQ_NO,
                                                                               value="000001")
            op_param_nhais_cypher = creators.create_parameter_with_binding(name=ParameterName.NHAIS_CYPHER, value="XX1")
            op_param_transaction_number = creators.create_parameter_with_binding(name=ParameterName.TRANSACTION_NO,
                                                                                 value="17")
            practitioner = fixtures.create_simple_practitioner()
            patient = fixtures.create_simple_patient()
            op_param_practitioner = creators.create_parameter_with_resource_ref(
                name=ParameterName.REGISTER_PRACTITIONER,
                resource_type=ResourceType.PRACTITIONER,
                reference="practitioner-1")
            op_param_patient = creators.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PATIENT,
                                                                           resource_type=ResourceType.PATIENT,
                                                                           reference="patient-1")
            op_def = creators.create_operation_definition(name=OperationName.REGISTER_BIRTH, code="gpc.registerpatient",
                                                          date_time="2019-04-23 09:00:04.159338",
                                                          contained=[practitioner, patient],
                                                          parameters=[op_param_message_sequence,
                                                                      op_param_transaction_number,
                                                                      op_param_nhais_cypher,
                                                                      op_param_practitioner, op_param_patient])

            message = message_adaptor.create_message(fhir_operation=op_def)

            compare(message, expected)
