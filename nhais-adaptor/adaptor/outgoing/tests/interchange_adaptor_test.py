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

            expected_edifact_interchange = ("UNB+UNOA:2+TES5+XX11+190423:0900+000001++FHSREG'"
                                            "UNH+000001+FHSREG:0:1:FH:FHS001'"
                                            "BGM+++507'"
                                            "NAD+FHS+XX1:954'"
                                            "DTM+137:201904230900:203'"
                                            "RFF+950:G1'"
                                            "S01+1'"
                                            "RFF+TN:17'"
                                            "NAD+GP+4826940,281:900'"
                                            "HEA+ACD+A:ZZZ'"
                                            "HEA+ATP+1:ZZZ'"
                                            "DTM+956:20190423:102'"
                                            "LOC+950+SPIDEY TOWN'"
                                            "S02+2'"
                                            "PNA+PAT+NHSNO11111:OPI+++SU:PARKER+FO:PETER+TI:MR'"
                                            "DTM+329:20190420:102'"
                                            "PDI+1'"
                                            "NAD+PAT++:1 SPIDEY WAY::SPIDEY TOWN:+++++SP1 1AA'"
                                            "UNT+18+000001'"
                                            "UNZ+1+000001'")

            interchange = InterchangeAdaptor.create_interchange(fhir_operation=op_def)

            compare(interchange, expected_edifact_interchange)
