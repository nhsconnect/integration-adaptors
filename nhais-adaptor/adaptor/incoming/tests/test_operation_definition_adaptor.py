import unittest
from testfixtures import compare
from adaptor.incoming.operation_definition_adaptor import OperationDefinitionAdaptor
from edifact.incoming.models.interchange import Interchange, InterchangeHeader
from edifact.incoming.models.message import Messages, MessageSegment, MessageSegmentBeginningDetails, \
    MessageSegmentRegistrationDetails, MessageSegmentPatientDetails
import adaptor.incoming.tests.fixtures as fixtures
from adaptor.incoming.config import reference_dict


class TestOperationDefinitionAdaptor(unittest.TestCase):
    """
    Test the conversion of an incoming edifact interchange to a fhir operation definition response
    """
    def test_format_date_time(self):
        """
        Tests the function that formats the edifact date time stamp to a fhir format
        """
        formatted_date = OperationDefinitionAdaptor.format_date_time("190501:0902")
        self.assertEqual(formatted_date, "2019-05-01 09:02")

    def test_create_operation_definition(self):
        """
        Tests the function to create a fhir operation definition from an incoming edifact interchange
        """
        with self.subTest("adapt an interchange with one message to a single fhir operation definition"):
            op_def = fixtures.create_operation_definition_for_approval(recipient="TES5", transaction_number="17")
            expected = [("17", "TES5", op_def)]

            interchange_header = InterchangeHeader(sender="XX11", recipient="TES5", date_time="190429:1756")
            messages = Messages([MessageSegment(MessageSegmentBeginningDetails(reference_number="F4"),
                                                MessageSegmentRegistrationDetails(transaction_number="17"))])
            incoming_interchange = Interchange(header=interchange_header, messages=messages)

            adaptor = OperationDefinitionAdaptor(reference_dict=reference_dict)
            op_defs = adaptor.create_operation_definition(interchange=incoming_interchange)

            compare(op_defs, expected)

        with self.subTest("adapt an interchange with two messages to two separate fhir operation definition"):
            op_def_1 = fixtures.create_operation_definition_for_approval(recipient="TES5",
                                                                         transaction_number="17")
            op_def_2 = fixtures.create_operation_definition_for_approval(recipient="TES5",
                                                                         transaction_number="18")
            expected = [("17", "TES5", op_def_1), ("18", "TES5", op_def_2)]

            interchange_header = InterchangeHeader(sender="XX11", recipient="TES5", date_time="190429:1756")
            messages = Messages([
                MessageSegment(MessageSegmentBeginningDetails(reference_number="F4"),
                               MessageSegmentRegistrationDetails(transaction_number="17")),
                MessageSegment(MessageSegmentBeginningDetails(reference_number="F4"),
                               MessageSegmentRegistrationDetails(transaction_number="18"))])

            incoming_interchange = Interchange(header=interchange_header, messages=messages)

            adaptor = OperationDefinitionAdaptor(reference_dict=reference_dict)
            op_defs = adaptor.create_operation_definition(interchange=incoming_interchange)

            compare(op_defs, expected)

        with self.subTest("adapt an interchange for a deduction"):
            op_def = fixtures.create_operation_definition_for_deduction(recipient="TES5", transaction_number="17",
                                                                        nhs_number="NHSNO22222")
            expected = [("17", "TES5", op_def)]

            interchange_header = InterchangeHeader(sender="XX11", recipient="TES5", date_time="190429:1756")
            messages = Messages([MessageSegment(MessageSegmentBeginningDetails(reference_number="F2"),
                                                MessageSegmentRegistrationDetails(transaction_number="17"),
                                                MessageSegmentPatientDetails(nhs_number="NHSNO22222"))])
            incoming_interchange = Interchange(header=interchange_header, messages=messages)

            adaptor = OperationDefinitionAdaptor(reference_dict=reference_dict)
            op_defs = adaptor.create_operation_definition(interchange=incoming_interchange)

            compare(op_defs, expected)
