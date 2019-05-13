import unittest

from testfixtures import compare

import adaptor.incoming.tests.fixtures as fixtures
from adaptor.incoming.config import reference_dict
from adaptor.incoming.operation_definition_adaptor import OperationDefinitionAdaptor
from edifact.incoming.models.interchange import Interchange, InterchangeHeader
from edifact.incoming.models.message import Messages, MessageSegment, MessageSegmentBeginningDetails
from edifact.incoming.models.transaction import Transactions, Transaction, TransactionRegistrationDetails, \
    TransactionPatientDetails


class TestOperationDefinitionAdaptor(unittest.TestCase):
    """
    Test the conversion of an incoming edifact interchange to a fhir operation definition response
    """

    def test_create_operation_definition(self):
        """
        Tests the function to create a fhir operation definition from an incoming edifact interchange
        """
        with self.subTest(
                "adapt an interchange with one message and transaction to a single fhir operation definition"):
            op_def = fixtures.create_operation_definition_for_approval(recipient="TES5", transaction_number="17")
            expected = [("17", "TES5", op_def)]

            incoming_interchange = Interchange(InterchangeHeader("XX11", "TES5", "190429:1756"),
                                               Messages([
                                                   MessageSegment(MessageSegmentBeginningDetails("F4"),
                                                                  Transactions([
                                                                      Transaction(
                                                                          TransactionRegistrationDetails("17")
                                                                      )
                                                                  ]))
                                               ]))

            adaptor = OperationDefinitionAdaptor(reference_dict=reference_dict)
            op_defs = adaptor.create_operation_definition(interchange=incoming_interchange)

            compare(op_defs, expected)

        with self.subTest("adapt an interchange one message but 2 transactions to two fhir operation definitions"):
            op_def_1 = fixtures.create_operation_definition_for_approval(recipient="TES5",
                                                                         transaction_number="17")
            op_def_2 = fixtures.create_operation_definition_for_approval(recipient="TES5",
                                                                         transaction_number="18")
            expected = [("17", "TES5", op_def_1), ("18", "TES5", op_def_2)]

            incoming_interchange = Interchange(InterchangeHeader("XX11", "TES5", "190429:1756"),
                                               Messages([
                                                   MessageSegment(MessageSegmentBeginningDetails("F4"),
                                                                  Transactions([
                                                                      Transaction(
                                                                          TransactionRegistrationDetails("17")
                                                                      ),
                                                                      Transaction(
                                                                          TransactionRegistrationDetails("18")
                                                                      )
                                                                  ]))
                                               ]))

            adaptor = OperationDefinitionAdaptor(reference_dict=reference_dict)
            op_defs = adaptor.create_operation_definition(interchange=incoming_interchange)

            compare(op_defs, expected)

        with self.subTest("adapt an interchange for a deduction"):
            op_def = fixtures.create_operation_definition_for_deduction(recipient="TES5", transaction_number="17",
                                                                        nhs_number="NHSNO22222")
            expected = [("17", "TES5", op_def)]

            incoming_interchange = Interchange(InterchangeHeader("XX11", "TES5", "190429:1756"),
                                               Messages([
                                                   MessageSegment(MessageSegmentBeginningDetails("F2"),
                                                                  Transactions([
                                                                      Transaction(
                                                                          TransactionRegistrationDetails("17"),
                                                                          TransactionPatientDetails("NHSNO22222")
                                                                      )
                                                                  ]))
                                               ]))

            adaptor = OperationDefinitionAdaptor(reference_dict=reference_dict)
            op_defs = adaptor.create_operation_definition(interchange=incoming_interchange)

            compare(op_defs, expected)

        with self.subTest("adapt an interchange with a message for a birth registration and a death registration "
                          "both with 2 transactions should result in 4 fhir operation definitions"):
            approval_1 = fixtures.create_operation_definition_for_approval(recipient="TES5",
                                                                           transaction_number="17")
            approval_2 = fixtures.create_operation_definition_for_approval(recipient="TES5",
                                                                           transaction_number="18")
            deduction_1 = fixtures.create_operation_definition_for_deduction(recipient="TES5",
                                                                             transaction_number="19",
                                                                             nhs_number="NHSNO11111")
            deduction_2 = fixtures.create_operation_definition_for_deduction(recipient="TES5",
                                                                             transaction_number="20",
                                                                             nhs_number="NHSNO22222")
            expected = [("17", "TES5", approval_1), ("18", "TES5", approval_2),
                        ("19", "TES5", deduction_1), ("20", "TES5", deduction_2)]

            incoming_interchange = Interchange(InterchangeHeader("XX11", "TES5", "190429:1756"),
                                               Messages([
                                                   MessageSegment(MessageSegmentBeginningDetails("F4"),
                                                                  Transactions([
                                                                      Transaction(
                                                                          TransactionRegistrationDetails("17")
                                                                      ),
                                                                      Transaction(
                                                                          TransactionRegistrationDetails("18")
                                                                      )
                                                                  ])),
                                                   MessageSegment(MessageSegmentBeginningDetails("F2"),
                                                                  Transactions([
                                                                      Transaction(
                                                                          TransactionRegistrationDetails("19"),
                                                                          TransactionPatientDetails("NHSNO11111")
                                                                      ),
                                                                      Transaction(
                                                                          TransactionRegistrationDetails("20"),
                                                                          TransactionPatientDetails("NHSNO22222")
                                                                      )
                                                                  ]))
                                               ]))

            adaptor = OperationDefinitionAdaptor(reference_dict=reference_dict)
            op_defs = adaptor.create_operation_definition(interchange=incoming_interchange)

            compare(op_defs, expected)
