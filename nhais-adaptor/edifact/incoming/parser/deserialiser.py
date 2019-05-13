from typing import List

import edifact.incoming.parser.creators as creators
from edifact.incoming.models.interchange import Interchange, InterchangeHeader
from edifact.incoming.models.message import MessageSegment, Messages, MessageSegmentBeginningDetails
from edifact.incoming.models.transaction import Transaction, Transactions, TransactionRegistrationDetails, \
    TransactionPatientDetails
from edifact.incoming.parser import EdifactDict
import edifact.incoming.parser.helpers as helpers

INTERCHANGE_HEADER_KEY = "UNB"
MESSAGE_HEADER_KEY = "UNH"
MESSAGE_BEGINNING_KEY = "BGM"
MESSAGE_REGISTRATION_KEY = "S01"
MESSAGE_PATIENT_KEY = "S02"
MESSAGE_TRAILER_KEY = "UNT"
INTERCHANGE_TRAILER_KEY = "UNZ"


def deserialise_interchange_header(original_dict: EdifactDict, index: int) -> InterchangeHeader:
    interchange_header_line = EdifactDict(helpers.extract_relevant_lines(original_dict, index, [MESSAGE_HEADER_KEY]))
    interchange_header = creators.create_interchange_header(interchange_header_line)
    return interchange_header


def deserialise_message_beginning(original_dict: EdifactDict, index: int) -> MessageSegmentBeginningDetails:
    msg_bgn_lines = EdifactDict(helpers.extract_relevant_lines(original_dict, index, [MESSAGE_REGISTRATION_KEY]))
    msg_bgn_details = creators.create_message_segment_beginning(msg_bgn_lines)
    return msg_bgn_details


def get_transaction_lines(original_dict: EdifactDict, index: int) -> EdifactDict:
    """
    From the original dict provided get the lines that represent a transaction within a message.
    This can be when another MESSAGE_REGISTRATION_KEY is found representing a new transaction or
    when the MESSAGE_TRAILER_KEY is found.
    In order to skip the first SO1 in the original_dict provided here the index is started at +1
    """
    transaction_lines = EdifactDict(
        helpers.extract_relevant_lines(original_dict, index + 1, [MESSAGE_REGISTRATION_KEY, MESSAGE_TRAILER_KEY]))
    return transaction_lines


def deserialise_registration(transaction_lines: EdifactDict) -> TransactionRegistrationDetails:
    registration_lines = EdifactDict(helpers.extract_relevant_lines(transaction_lines, 0,
                                                                    [MESSAGE_REGISTRATION_KEY, MESSAGE_PATIENT_KEY,
                                                                     MESSAGE_TRAILER_KEY]))
    transaction_reg = creators.create_transaction_registration(registration_lines)
    return transaction_reg


def find_index_of_patient_segment(transaction_lines: EdifactDict) -> int:
    index_of_patient_segment = -1
    for index, line in enumerate(transaction_lines):
        if line[0] == MESSAGE_PATIENT_KEY:
            index_of_patient_segment = index
    return index_of_patient_segment


def does_transaction_have_patient_segment(transaction_lines: EdifactDict) -> bool:
    has_patient_segment = True if find_index_of_patient_segment(transaction_lines) != -1 else False
    return has_patient_segment


def deserialise_patient_if_applicable(transaction_lines: EdifactDict) -> TransactionPatientDetails:
    transaction_pat = None
    if does_transaction_have_patient_segment(transaction_lines):
        patient_lines = EdifactDict(helpers.extract_relevant_lines(transaction_lines,
                                                                   find_index_of_patient_segment(transaction_lines),
                                                                   [MESSAGE_REGISTRATION_KEY, MESSAGE_TRAILER_KEY]))
        transaction_pat = creators.create_transaction_patient(patient_lines)

    return transaction_pat


def deserialise_transaction(original_dict: EdifactDict, index: int) -> Transaction:

    transaction_lines = get_transaction_lines(original_dict, index)

    transaction_reg = deserialise_registration(transaction_lines)

    transaction_pat = deserialise_patient_if_applicable(transaction_lines)

    transaction = Transaction(transaction_reg, transaction_pat)
    return transaction


def convert(lines: List[str]) -> Interchange:
    """
    Takes the original list of edifact lines and converts to a deserialised representation.
    Only relevant information from the edifact message is extracted and populated in the models.
    :param lines: A list of string of the edifact lines.
    :return: Interchange: The incoming representation of the edifact interchange.
    """
    original_dict = helpers.convert_to_dict(lines)
    messages = []
    transactions = []
    interchange = None
    interchange_header = None
    msg_bgn_details = None

    for index, line in enumerate(original_dict):
        key = line[0]

        if key == INTERCHANGE_HEADER_KEY:
            interchange_header = deserialise_interchange_header(original_dict, index)

        elif key == MESSAGE_BEGINNING_KEY:
            msg_bgn_details = deserialise_message_beginning(original_dict, index)

        elif key == MESSAGE_REGISTRATION_KEY:
            transaction = deserialise_transaction(original_dict, index)
            transactions.append(transaction)

        elif key == MESSAGE_TRAILER_KEY:
            msg = MessageSegment(msg_bgn_details, Transactions(transactions))
            messages.append(msg)
            transactions = []

        elif key == INTERCHANGE_TRAILER_KEY:
            interchange = Interchange(interchange_header, Messages(messages))

    return interchange
