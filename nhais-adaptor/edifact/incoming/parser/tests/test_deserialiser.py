import unittest

from testfixtures import compare

import edifact.incoming.parser.deserialiser as deserialiser
from edifact.incoming.models.interchange import InterchangeHeader, Interchange
from edifact.incoming.models.message import MessageSegmentBeginningDetails, MessageSegment, Messages
from edifact.incoming.models.transaction import Transactions, Transaction, TransactionRegistrationDetails, \
    TransactionPatientDetails
import edifact.incoming.parser.tests.fixtures as fixtures


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

            input_lines = []
            input_lines.extend(fixtures.create_interchange_header_line())
            input_lines.extend(fixtures.create_message_header_line())
            input_lines.extend(fixtures.create_message_beginning_lines("F4"))
            input_lines.extend(fixtures.create_transaction_registration_lines("211102"))
            input_lines.extend(fixtures.create_message_trailer_line())
            input_lines.extend(fixtures.create_interchange_trailer_line())

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

            input_lines = []
            input_lines.extend(fixtures.create_interchange_header_line())
            input_lines.extend(fixtures.create_message_header_line())
            input_lines.extend(fixtures.create_message_beginning_lines("F4"))
            input_lines.extend(fixtures.create_transaction_registration_lines("211102"))
            input_lines.extend(fixtures.create_transaction_patient_lines("9876556789"))
            input_lines.extend(fixtures.create_message_trailer_line())
            input_lines.extend(fixtures.create_interchange_trailer_line())

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

            input_lines = []
            input_lines.extend(fixtures.create_interchange_header_line())
            input_lines.extend(fixtures.create_message_header_line())
            input_lines.extend(fixtures.create_message_beginning_lines("F4"))
            input_lines.extend(fixtures.create_transaction_registration_lines("211102"))
            input_lines.extend(fixtures.create_transaction_patient_lines("9876556789"))
            input_lines.extend(fixtures.create_transaction_registration_lines("211103"))
            input_lines.extend(fixtures.create_message_trailer_line())
            input_lines.extend(fixtures.create_interchange_trailer_line())

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

            input_lines = []
            input_lines.extend(fixtures.create_interchange_header_line())
            input_lines.extend(fixtures.create_message_header_line())
            input_lines.extend(fixtures.create_message_beginning_lines("F4"))
            input_lines.extend(fixtures.create_transaction_registration_lines("211102"))
            input_lines.extend(fixtures.create_transaction_patient_lines("9876556789"))
            input_lines.extend(fixtures.create_transaction_registration_lines("211103"))
            input_lines.extend(fixtures.create_message_trailer_line())
            input_lines.extend(fixtures.create_message_header_line())
            input_lines.extend(fixtures.create_message_beginning_lines("F2"))
            input_lines.extend(fixtures.create_transaction_registration_lines("211104"))
            input_lines.extend(fixtures.create_transaction_patient_lines("111111111"))
            input_lines.extend(fixtures.create_transaction_registration_lines("211105"))
            input_lines.extend(fixtures.create_transaction_patient_lines("2222222222"))
            input_lines.extend(fixtures.create_message_trailer_line())
            input_lines.extend(fixtures.create_interchange_trailer_line())

            result = deserialiser.convert(input_lines)
            compare(result, expected)
