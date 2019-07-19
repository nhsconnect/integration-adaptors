import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities

import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.ebxml_request_envelope as ebxml_request_envelope

EXPECTED_MESSAGES_DIR = "expected_messages"
EXPECTED_EBXML = "ebxml_request.xml"

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"

MESSAGE_DIR = "test_messages"
CONTENT_TYPE_HEADER_NAME = "Content-Type"
MULTIPART_MIME_HEADERS = {CONTENT_TYPE_HEADER_NAME: 'multipart/related; boundary="--=_MIME-Boundary"'}
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
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'


def expected_values(message=None):
    values = EXPECTED_VALUES.copy()

    if message:
        values[ebxml_request_envelope.MESSAGE] = message

    return values


class TestEbxmlRequestEnvelope(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_message_dir = Path(current_dir) / EXPECTED_MESSAGES_DIR
    message_dir = Path(current_dir) / MESSAGE_DIR

    def setUp(self):
        self.envelope = ebxml_request_envelope.EbxmlRequestEnvelope({
            ebxml_envelope.FROM_PARTY_ID: "TESTGEN-201324",
            ebxml_envelope.TO_PARTY_ID: "YEA-0000806",
            ebxml_envelope.CPA_ID: "S1001A1630",
            ebxml_envelope.CONVERSATION_ID: "79F49A34-9798-404C-AEC4-FD38DD81C138",
            ebxml_envelope.SERVICE: "urn:nhs:names:services:pdsquery",
            ebxml_envelope.ACTION: "QUPA_IN000006UK02",
            ebxml_envelope.DUPLICATE_ELIMINATION: True,
            ebxml_envelope.ACK_REQUESTED: True,
            ebxml_envelope.ACK_SOAP_ACTOR: "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
            ebxml_envelope.SYNC_REPLY: True,
            ebxml_request_envelope.MESSAGE: '<QUPA_IN000006UK02 xmlns="urn:hl7-org:v3"></QUPA_IN000006UK02>'
        })

    @patch.object(MessageUtilities, "get_timestamp")
    @patch.object(MessageUtilities, "get_uuid")
    def test_build_message(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = MOCK_UUID
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_message = FileUtilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))

        message_id, message = self.envelope.serialize()

        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of both strings
        normalized_expected_message = FileUtilities.normalize_line_endings(expected_message)
        normalized_message = FileUtilities.normalize_line_endings(message)

        self.assertEqual(MOCK_UUID, message_id)
        self.assertEqual(normalized_expected_message, normalized_message)

    def test_from_string(self):
        # TODO: Extract a super-class for common test functionality

        with self.subTest("A valid request containing a payload"):
            message = FileUtilities.get_file_string(str(self.message_dir / "ebxml_request.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest("An invalid multi-part MIME message"):
            message = FileUtilities.get_file_string(str(self.message_dir / "ebxml_request_no_header.msg"))

            with (self.assertRaises(ebxml_request_envelope.EbXmlParsingError)):
                ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

        with self.subTest("A valid request that does not contain the optional payload MIME part"):
            message = FileUtilities.get_file_string(str(self.message_dir / "ebxml_request_no_payload.msg"))
            expected_values_with_no_payload = expected_values()

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_no_payload, parsed_message.message_dictionary)

        with self.subTest("A valid request containing an additional MIME part"):
            message = FileUtilities.get_file_string(str(self.message_dir / "ebxml_request_additional_attachment.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest("An message that is not a multi-part MIME message"):
            with (self.assertRaises(ebxml_request_envelope.EbXmlParsingError)):
                ebxml_request_envelope.EbxmlRequestEnvelope.from_string({CONTENT_TYPE_HEADER_NAME: "text/plain"},
                                                                        "A message")
