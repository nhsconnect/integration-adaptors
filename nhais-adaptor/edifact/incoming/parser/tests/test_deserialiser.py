import unittest

from testfixtures import compare

import edifact.incoming.parser.deserialiser as deserialiser
from edifact.incoming.models.interchange import InterchangeHeader, Interchange
from edifact.incoming.models.message import MessageSegmentBeginningDetails, MessageSegment, Messages
from edifact.incoming.models.transaction import Transactions, Transaction, TransactionRegistrationDetails, \
    TransactionPatientDetails
import edifact.incoming.parser.tests.fixtures as fixtures
from edifact.incoming.parser.tests.fixtures import LineBuilder


class TestDeserialiser(unittest.TestCase):
    def test_convert(self):
        with self.subTest("When the edifact incoming message does not have a patient section (S02)"):
            expected = Interchange(InterchangeHeader("SO01", "ROO5", "190429:1756"),
                                   Messages([
                                       MessageSegment(MessageSegmentBeginningDetails("F4"),
                                                      Transactions([
                                                          Transaction(
                                                              TransactionRegistrationDetails("211102")
                                                          )
                                                      ]))
                                   ]))

            input_lines = LineBuilder().start_interchange().start_message("F4")\
                .add_transaction("211102").end_message().end_interchange().build()

            result = deserialiser.convert(input_lines)
            compare(result, expected)

        with self.subTest("When the edifact incoming message does have a patient section (SO2)"):
            expected = Interchange(InterchangeHeader("SO01", "ROO5", "190429:1756"),
                                   Messages([
                                       MessageSegment(MessageSegmentBeginningDetails("F4"),
                                                      Transactions([
                                                          Transaction(
                                                              TransactionRegistrationDetails("211102"),
                                                              TransactionPatientDetails("9876556789")
                                                          )
                                                      ]))
                                   ]))

            input_lines = LineBuilder().start_interchange().start_message("F4")\
                .add_transaction("211102", "9876556789").end_message().end_interchange().build()

            result = deserialiser.convert(input_lines)
            compare(result, expected)

        with self.subTest("When the edifact incoming interchange has a message with multiple transactions"):
            expected = Interchange(InterchangeHeader("SO01", "ROO5", "190429:1756"),
                                   Messages([
                                       MessageSegment(MessageSegmentBeginningDetails("F4"),
                                                      Transactions([
                                                          Transaction(
                                                              TransactionRegistrationDetails("211102"),
                                                              TransactionPatientDetails("9876556789")
                                                          ),
                                                          Transaction(
                                                              TransactionRegistrationDetails("211103")
                                                          ),
                                                      ]))
                                   ]))

            input_lines = LineBuilder().start_interchange().start_message("F4")\
                .add_transaction("211102", "9876556789").add_transaction("211103")\
                .end_message().end_interchange().build()

            result = deserialiser.convert(input_lines)
            compare(result, expected)

        with self.subTest("When the edifact incoming interchange has a 2 messages with multiple transactions"):
            expected = Interchange(InterchangeHeader("SO01", "ROO5", "190429:1756"),
                                   Messages([
                                       MessageSegment(MessageSegmentBeginningDetails("F4"),
                                                      Transactions([
                                                          Transaction(
                                                              TransactionRegistrationDetails("211102"),
                                                              TransactionPatientDetails("9876556789")
                                                          ),
                                                          Transaction(
                                                              TransactionRegistrationDetails("211103")
                                                          ),
                                                      ])),
                                       MessageSegment(MessageSegmentBeginningDetails("F2"),
                                                      Transactions([
                                                          Transaction(
                                                              TransactionRegistrationDetails("211104"),
                                                              TransactionPatientDetails("111111111")
                                                          ),
                                                          Transaction(
                                                              TransactionRegistrationDetails("211105"),
                                                              TransactionPatientDetails("2222222222")
                                                          ),
                                                      ]))
                                   ]))

            input_lines = LineBuilder().start_interchange().start_message("F4")\
                .add_transaction("211102", "9876556789").add_transaction("211103").end_message()\
                .start_message("F2").add_transaction("211104", "111111111").add_transaction("211105", "2222222222")\
                .end_message().end_interchange().build()

            result = deserialiser.convert(input_lines)
            compare(result, expected)
