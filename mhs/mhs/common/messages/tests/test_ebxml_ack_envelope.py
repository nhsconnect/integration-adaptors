import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities
from utilities.xml_utilities import XmlUtilities

import mhs.common.messages.ebxml_ack_envelope as ebxml_ack_envelope
import mhs.common.messages.ebxml_envelope as ebxml_envelope

EXPECTED_MESSAGES_DIR = "expected_messages"
EXPECTED_EBXML = "ebxml_ack.xml"

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


class TestEbXmlAckEnvelope(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_message_dir = Path(current_dir) / EXPECTED_MESSAGES_DIR
    message_dir = Path(current_dir) / MESSAGE_DIR

    @patch.object(MessageUtilities, "get_timestamp")
    @patch.object(MessageUtilities, "get_uuid")
    def test_build_message(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = MOCK_UUID
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_message = FileUtilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))

        envelope = ebxml_ack_envelope.EbxmlAckEnvelope({
            ebxml_envelope.FROM_PARTY_ID: "TESTGEN-201324",
            ebxml_envelope.TO_PARTY_ID: "YEA-0000806",
            ebxml_envelope.CPA_ID: "S1001A1630",
            ebxml_envelope.CONVERSATION_ID: "79F49A34-9798-404C-AEC4-FD38DD81C138",
            ebxml_ack_envelope.RECEIVED_MESSAGE_TIMESTAMP: "2013-04-16T07:52:09Z",
            ebxml_ack_envelope.RECEIVED_MESSAGE_ID: "0CDBA95F-74DA-47E9-8383-7B8E9167D146",
        })

        message_id, message = envelope.serialize()

        expected_message_bytes = expected_message.encode()
        message_bytes = message.encode()

        self.assertEqual(MOCK_UUID, message_id)
        XmlUtilities.assert_xml_equal(expected_message_bytes, message_bytes)

    def test_from_string(self):
        message = FileUtilities.get_file_string(str(self.message_dir / "ebxml_header.xml"))

        parsed_message = ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, message)

        self.assertEqual(EXPECTED_VALUES, parsed_message.message_dictionary)

    def test_from_string_with_no_values(self):
        message = FileUtilities.get_file_string(str(self.message_dir / "ebxml_header_empty.xml"))

        parsed_message = ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, message)

        self.assertEqual({}, parsed_message.message_dictionary)
