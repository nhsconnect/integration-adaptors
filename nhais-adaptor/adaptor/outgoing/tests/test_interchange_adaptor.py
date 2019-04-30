import unittest
from testfixtures import compare
from adaptor.outgoing.interchange_adaptor import InterchangeAdaptor
from adaptor.outgoing.fhir_helpers.operation_definition import OperationDefinitionHelper as odh
from adaptor.outgoing.fhir_helpers.tests.fixtures import create_simple_patient, create_simple_practitioner
from adaptor.outgoing.fhir_helpers.constants import ParameterName, ResourceType, OperationName


class InterchangeAdaptorTest(unittest.TestCase):
    """
    Test the conversation of fhir to an edifact interchange
    """

    def test_create_interchange(self):
        """
        Test the function to create an edifact interchange
        """
        with self.subTest("When the operation is for a Birth Registration"):
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

            op_param_interchange_sequence = odh.create_parameter_with_binding(name=ParameterName.INTERCHANGE_SEQ_NO,
                                                                              value="000001")
            op_param_sender_cypher = odh.create_parameter_with_binding(name=ParameterName.SENDER_CYPHER, value="TES5")
            op_param_message_sequence = odh.create_parameter_with_binding(name=ParameterName.MESSAGE_SEQ_NO,
                                                                          value="000001")
            op_param_nhais_cypher = odh.create_parameter_with_binding(name=ParameterName.NHAIS_CYPHER, value="XX1")
            op_param_transaction_number = odh.create_parameter_with_binding(name=ParameterName.TRANSACTION_NO,
                                                                            value="17")
            practitioner = create_simple_practitioner()
            patient = create_simple_patient()
            op_param_practitioner = odh.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PRACTITIONER,
                                                                           resource_type=ResourceType.PRACTITIONER,
                                                                           reference="practitioner-1")
            op_param_patient = odh.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PATIENT,
                                                                      resource_type=ResourceType.PATIENT,
                                                                      reference="patient-1")
            op_def = odh.create_operation_definition(name=OperationName.REGISTER_BIRTH,
                                                     code="gpc.registerpatient",
                                                     date_time="2019-04-23 09:00:04.159338",
                                                     contained=[practitioner, patient],
                                                     parameter=[op_param_interchange_sequence,
                                                                op_param_sender_cypher,
                                                                op_param_message_sequence,
                                                                op_param_transaction_number,
                                                                op_param_nhais_cypher,
                                                                op_param_practitioner, op_param_patient])

            interchange = InterchangeAdaptor.create_interchange(fhir_operation=op_def)

            compare(interchange, expected_edifact_interchange)
