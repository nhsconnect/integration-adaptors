from unittest.mock import patch

from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities

import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.ebxml_request_envelope as ebxml_request_envelope
import mhs.common.messages.tests.test_ebxml_envelope as test_ebxml_envelope

EXPECTED_EBXML = "ebxml_request.xml"

CONTENT_TYPE_HEADER_NAME = "Content-Type"
MULTIPART_MIME_HEADERS = {CONTENT_TYPE_HEADER_NAME: 'multipart/related; boundary="--=_MIME-Boundary"'}
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'


def expected_values(message=None):
    values = test_ebxml_envelope.EXPECTED_VALUES.copy()

    if message:
        values[ebxml_request_envelope.MESSAGE] = message

    return values


class TestEbxmlRequestEnvelope(test_ebxml_envelope.TestEbxmlEnvelope):

    @patch.object(MessageUtilities, "get_timestamp")
    @patch.object(MessageUtilities, "get_uuid")
    def test_build_message(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_message = FileUtilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))

        envelope = ebxml_request_envelope.EbxmlRequestEnvelope({
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

        message_id, message = envelope.serialize()

        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of both strings
        normalized_expected_message = FileUtilities.normalize_line_endings(expected_message)
        normalized_message = FileUtilities.normalize_line_endings(message)

        self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
        self.assertEqual(normalized_expected_message, normalized_message)

    def test_from_string(self):
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
