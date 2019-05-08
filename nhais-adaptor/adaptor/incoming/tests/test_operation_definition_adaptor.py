import unittest
from testfixtures import compare
import adaptor.incoming.operation_definition_adaptor as incoming_adaptor
from edifact.incoming.models.interchange import Interchange, InterchangeHeader
from edifact.incoming.models.message import Messages, MessageSegment, MessageSegmentBeginningDetails, \
    MessageSegmentRegistrationDetails
import adaptor.incoming.tests.fixtures as fixtures


class TestOperationDefinitionAdaptor(unittest.TestCase):
    """
    Test the conversion of an incoming edifact interchange to a fhir operation definition response
    """

    def test_format_date_time(self):
        """
        Tests the function that formats the edifact date time stamp to a fhir format
        """
        formatted_date = incoming_adaptor.format_date_time("190501:0902")
        self.assertEqual(formatted_date, "2019-05-01 09:02")

    def test_create_operation_definition(self):
        """
        Tests the function to create a fhir operation definition from an incoming edifact interchange
        """
        with self.subTest("adapt an interchange with one message to a single fhir operation definition"):
            op_def = fixtures.create_operation_definition_for_birth_approval(recipient="TES5", transaction_number="17")
            expected = [("17", "TES5", op_def)]

            interchange_header = InterchangeHeader(sender="XX11", recipient="TES5", date_time="190429:1756")
            messages = Messages([MessageSegment(MessageSegmentBeginningDetails(reference_number="F4"),
                                                MessageSegmentRegistrationDetails(transaction_number="17"))])
            incoming_interchange = Interchange(header=interchange_header, messages=messages)

            op_defs = incoming_adaptor.create_operation_definition(incoming_interchange)

            compare(op_defs, expected)

        with self.subTest("adapt an interchange with two messages to two separate fhir operation definition"):
            op_def_1 = fixtures.create_operation_definition_for_birth_approval(recipient="TES5",
                                                                               transaction_number="17")
            op_def_2 = fixtures.create_operation_definition_for_birth_approval(recipient="TES5",
                                                                               transaction_number="18")
            expected = [("17", "TES5", op_def_1), ("18", "TES5", op_def_2)]

            interchange_header = InterchangeHeader(sender="XX11", recipient="TES5", date_time="190429:1756")
            messages = Messages([
                MessageSegment(MessageSegmentBeginningDetails(reference_number="F4"),
                               MessageSegmentRegistrationDetails(transaction_number="17")),
                MessageSegment(MessageSegmentBeginningDetails(reference_number="F4"),
                               MessageSegmentRegistrationDetails(transaction_number="18"))])

            incoming_interchange = Interchange(header=interchange_header, messages=messages)

            op_defs = incoming_adaptor.create_operation_definition(incoming_interchange)

            compare(op_defs, expected)
