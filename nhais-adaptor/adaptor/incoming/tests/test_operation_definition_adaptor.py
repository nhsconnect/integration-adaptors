import unittest
from testfixtures import compare
import adaptor.incoming.operation_definition_adaptor as incoming_adaptor
from edifact.incoming.models.interchange import Interchange, InterchangeHeader
from edifact.incoming.models.message import Messages, MessageSegment, MessageSegmentBeginningDetails, \
    MessageSegmentRegistrationDetails
import adaptor.fhir_helpers.fhir_creators as creators


class TestOperationDefinitionAdaptor(unittest.TestCase):
    """
    Test the conversion of an incoming edifact interchange to a fhir operation definition response
    """

    def test_create_operation_definition(self):
        """
        Tests the function to create a fhir operation definition from an incoming edifact interchange
        """
        sender_parameter = creators.create_parameter_with_binding(name="senderCypher", value="XX11", direction="out")
        recipient_parameter = creators.create_parameter_with_binding(name="recipientCypher", value="TES5",
                                                                     direction="out")
        transaction_parameter = creators.create_parameter_with_binding(name="transactionNumber", value="17",
                                                                       direction="out")
        expected = creators.create_operation_definition(name="Response-RegisterPatient-Approval",
                                                        code="gpc.registerpatient.approval",
                                                        date_time="2019-04-29 17:56",
                                                        contained=[],
                                                        parameters=[
                                                            sender_parameter,
                                                            recipient_parameter,
                                                            transaction_parameter
                                                        ])

        interchange_header = InterchangeHeader(sender="XX11", recipient="TES5", date_time="190429:1756")
        messages = Messages([MessageSegment(MessageSegmentBeginningDetails(reference_number="F4"),
                                            MessageSegmentRegistrationDetails(transaction_number="17"))])
        incoming_interchange = Interchange(header=interchange_header, messages=messages)

        op_def = incoming_adaptor.create_operation_definition(incoming_interchange)

        compare(op_def, expected)
