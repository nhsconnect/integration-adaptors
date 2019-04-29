import unittest
from testfixtures import compare
from adaptor.outgoing.interchange_adaptor import InterchangeAdaptor
from adaptor.outgoing.message_adaptor import MessageAdaptor
from adaptor.outgoing.fhir_helpers.operation_definition import OperationDefinitionHelper as odh
from adaptor.outgoing.fhir_helpers.tests.fixtures import Fixtures
from edifact.models.interchange import Interchange
from edifact.models.name import Name
from edifact.models.address import Address as EdifactAddress
from edifact.models.message import MessageSegmentPatientDetails, MessageSegmentRegistrationDetails, MessageBeginning, \
    Message, Messages


class InterchangeAdaptorTest(unittest.TestCase):
    """
    Test the conversation of fhir to an edifact interchange
    """

    def test_create_interchange(self):
        """
        Test the function to create an edifact interchange
        """
        with self.subTest("When the operation is for a Birth Registration"):
            op_param_interchange_sequence = odh.create_parameter_with_binding(name="interchangeSequenceNumber",
                                                                              value="000001")
            op_param_sender_cypher = odh.create_parameter_with_binding(name="senderCypher", value="TES5")
            op_param_message_sequence = odh.create_parameter_with_binding(name="messageSequenceNumber", value="000001")
            op_param_nhais_cypher = odh.create_parameter_with_binding(name="nhaisCypher", value="XX1")
            op_param_transaction_number = odh.create_parameter_with_binding(name="transactionNumber", value="17")

            practitioner = Fixtures.create_simple_practitioner()
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
                                                     parameter=[op_param_interchange_sequence,
                                                                op_param_sender_cypher,
                                                                op_param_message_sequence,
                                                                op_param_transaction_number,
                                                                op_param_nhais_cypher,
                                                                op_param_practitioner, op_param_patient])

            msg_bgn = MessageBeginning(party_id="XX1", date_time="2019-04-23 09:00:04.159338", ref_number="G1")
            edifact_pat_name = Name(family_name="Parker", first_given_forename="Peter", title="Mr")
            edifact_pat_address = EdifactAddress(address_line_1="1 Spidey Way", town="Spidey Town", post_code="SP1 1AA")
            msg_seg_pat_details = MessageSegmentPatientDetails(id_number="NHSNO11111", name=edifact_pat_name,
                                                               date_of_birth="2019-04-23",
                                                               gender="1", address=edifact_pat_address)
            msg_seg_reg_details = MessageSegmentRegistrationDetails(transaction_number=17,
                                                                    party_id="4826940,281",
                                                                    acceptance_code="A",
                                                                    acceptance_type=1,
                                                                    date_time="2019-04-23 09:00:04.159338",
                                                                    location="Spidey Town")
            msg = Message(sequence_number="000001", message_beginning=msg_bgn,
                          message_segment_registration_details=msg_seg_reg_details,
                          message_segment_patient_details=msg_seg_pat_details)

            msgs = Messages([msg])

            expected = Interchange(sender="TES5", recipient="XX11", date_time="2019-04-23 09:00:04.159338",
                                   sequence_number="000001",
                                   messages=msgs)

            interchange = InterchangeAdaptor.create_interchange(fhir_operation=op_def)

            compare(interchange, expected)
