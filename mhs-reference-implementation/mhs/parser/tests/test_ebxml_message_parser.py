import os
from pathlib import Path
from unittest import TestCase

from mhs.parser.ebxml_message_parser import EbXmlRequestMessageParser, FROM_PARTY_ID, TO_PARTY_ID, \
    CPA_ID, CONVERSATION_ID, SERVICE, ACTION, MESSAGE_ID, REF_TO_MESSAGE_ID, TIMESTAMP, DUPLICATE_ELIMINATION, \
    ACK_REQUESTED, ACK_SOAP_ACTOR, SYNC_REPLY, MESSAGE, EbXmlParsingError, EbXmlMessageParser
from utilities.file_utilities import FileUtilities

MESSAGE_DIR = "test_messages"
CONTENT_TYPE_HEADER_NAME = "Content-Type"
MULTIPART_MIME_HEADERS = {CONTENT_TYPE_HEADER_NAME: 'multipart/related; boundary="--=_MIME-Boundary"'}
EXPECTED_VALUES = {
    FROM_PARTY_ID: "YES-0000806",
    TO_PARTY_ID: "A91424-9199121",
    CPA_ID: "S1001A1630",
    CONVERSATION_ID: "10F5A436-1913-43F0-9F18-95EA0E43E61A",
    SERVICE: "urn:nhs:names:services:psis",
    ACTION: "MCCI_IN010000UK13",
    MESSAGE_ID: "C614484E-4B10-499A-9ACD-5D645CFACF61",
    REF_TO_MESSAGE_ID: "F106022D-758B-49A9-A80A-8FF211C32A43",
    TIMESTAMP: "2019-05-04T20:55:16Z",
    DUPLICATE_ELIMINATION: True,
    ACK_REQUESTED: True,
    ACK_SOAP_ACTOR: "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
    SYNC_REPLY: True,
}
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'

current_dir = os.path.dirname(os.path.abspath(__file__))
message_dir = Path(current_dir) / MESSAGE_DIR


def expected_values(message=None):
    values = EXPECTED_VALUES.copy()

    if message:
        values[MESSAGE] = message

    return values


class TestEbXmlMessageParser(TestCase):

    def setUp(self):
        self.parser = EbXmlMessageParser()

    def test_parse_message(self):
        message = FileUtilities.get_file_string(str(message_dir / "ebxml_header.xml"))
        expected_values_without_message = expected_values()

        extracted_values = self.parser.parse_message(MULTIPART_MIME_HEADERS, message)

        self.assertEqual(expected_values_without_message, extracted_values)

    def test_parse_message_with_no_values(self):
        message = FileUtilities.get_file_string(str(message_dir / "ebxml_header_empty.xml"))

        extracted_values = self.parser.parse_message(MULTIPART_MIME_HEADERS, message)

        self.assertEqual({}, extracted_values)


class TestEbXmlRequestMessageParser(TestCase):

    def setUp(self):
        self.parser = EbXmlRequestMessageParser()

    def test_parse_message(self):
        with self.subTest("A valid request containing a payload"):
            message = FileUtilities.get_file_string(str(message_dir / "ebxml_request.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)

            extracted_values = self.parser.parse_message(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, extracted_values)

        with self.subTest("An invalid multi-part MIME message"):
            message = FileUtilities.get_file_string(str(message_dir / "ebxml_request_no_header.msg"))

            with (self.assertRaises(EbXmlParsingError)):
                self.parser.parse_message(MULTIPART_MIME_HEADERS, message)

        with self.subTest("A valid request that does not contain the optional payload MIME part"):
            message = FileUtilities.get_file_string(str(message_dir / "ebxml_request_no_payload.msg"))
            expected_values_with_no_payload = expected_values()

            extracted_values = self.parser.parse_message(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_no_payload, extracted_values)

        with self.subTest("A valid request containing an additional MIME part"):
            message = FileUtilities.get_file_string(str(message_dir / "ebxml_request_additional_attachment.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)

            extracted_values = self.parser.parse_message(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, extracted_values)

        with self.subTest("An message that is not a multi-part MIME message"):
            with (self.assertRaises(EbXmlParsingError)):
                self.parser.parse_message({CONTENT_TYPE_HEADER_NAME: "text/plain"}, "A message")
