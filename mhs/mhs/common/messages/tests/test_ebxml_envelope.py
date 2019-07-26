import os
from pathlib import Path
from unittest import TestCase

import mhs.common.messages.ebxml_envelope as ebxml_envelope

EXPECTED_MESSAGES_DIR = "expected_messages"
MESSAGE_DIR = "test_messages"

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"

EXPECTED_VALUES = {
    ebxml_envelope.FROM_PARTY_ID: "YES-0000806",
    ebxml_envelope.TO_PARTY_ID: "A91424-9199121",
    ebxml_envelope.CPA_ID: "S1001A1630",
    ebxml_envelope.CONVERSATION_ID: "10F5A436-1913-43F0-9F18-95EA0E43E61A",
    ebxml_envelope.SERVICE: "urn:nhs:names:services:psis",
    ebxml_envelope.ACTION: "MCCI_IN010000UK13",
    ebxml_envelope.MESSAGE_ID: "C614484E-4B10-499A-9ACD-5D645CFACF61",
    ebxml_envelope.REF_TO_MESSAGE_ID: "F106022D-758B-49A9-A80A-8FF211C32A43",
    ebxml_envelope.TIMESTAMP: "2019-05-04T20:55:16Z",
    ebxml_envelope.DUPLICATE_ELIMINATION: True,
    ebxml_envelope.ACK_REQUESTED: True,
    ebxml_envelope.ACK_SOAP_ACTOR: "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
    ebxml_envelope.SYNC_REPLY: True,
}


class TestEbxmlEnvelope(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    message_dir = Path(current_dir) / MESSAGE_DIR
    expected_message_dir = Path(current_dir) / EXPECTED_MESSAGES_DIR
