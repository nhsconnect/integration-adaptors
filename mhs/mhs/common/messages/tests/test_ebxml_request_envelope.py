from unittest.mock import patch

import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.ebxml_request_envelope as ebxml_request_envelope
import mhs.common.messages.tests.test_ebxml_envelope as test_ebxml_envelope
from builder import pystache_message_builder
from utilities import file_utilities
from utilities import message_utilities

EXPECTED_EBXML = "ebxml_request.xml"

CONTENT_TYPE_HEADER_NAME = "Content-Type"
MULTIPART_MIME_HEADERS = {CONTENT_TYPE_HEADER_NAME: 'multipart/related; boundary="--=_MIME-Boundary"'}
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'

_ADDITIONAL_EXPECTED_VALUES = {
    ebxml_request_envelope.DUPLICATE_ELIMINATION: True,
    ebxml_request_envelope.ACK_REQUESTED: True,
    ebxml_request_envelope.ACK_SOAP_ACTOR: "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
    ebxml_request_envelope.SYNC_REPLY: True,
}
EXPECTED_VALUES = {**test_ebxml_envelope.BASE_EXPECTED_VALUES, **_ADDITIONAL_EXPECTED_VALUES}

EXPECTED_HTTP_HEADERS = {
    'charset': 'UTF-8',
    'SOAPAction': 'urn:nhs:names:services:pdsquery/QUPA_IN000006UK02',
    'Content-Type': 'multipart/related; boundary="--=_MIME-Boundary"; type=text/xml; start=ebXMLHeader@spine.nhs.uk'
}


def get_test_message_dictionary():
    return {
        ebxml_envelope.FROM_PARTY_ID: "TESTGEN-201324",
        ebxml_envelope.TO_PARTY_ID: "YEA-0000806",
        ebxml_envelope.CPA_ID: "S1001A1630",
        ebxml_envelope.CONVERSATION_ID: "79F49A34-9798-404C-AEC4-FD38DD81C138",
        ebxml_envelope.SERVICE: "urn:nhs:names:services:pdsquery",
        ebxml_envelope.ACTION: "QUPA_IN000006UK02",
        ebxml_request_envelope.DUPLICATE_ELIMINATION: True,
        ebxml_request_envelope.ACK_REQUESTED: True,
        ebxml_request_envelope.ACK_SOAP_ACTOR: "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
        ebxml_request_envelope.SYNC_REPLY: True,
        ebxml_request_envelope.MESSAGE: '<QUPA_IN000006UK02 xmlns="urn:hl7-org:v3"></QUPA_IN000006UK02>'
    }


def expected_values(message=None):
    values = EXPECTED_VALUES.copy()

    if message:
        values[ebxml_request_envelope.MESSAGE] = message

    return values


class TestEbxmlRequestEnvelope(test_ebxml_envelope.TestEbxmlEnvelope):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expected_message = file_utilities.FileUtilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))
        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of the strings being compared
        self.normalized_expected_serialized_message = file_utilities.FileUtilities.normalize_line_endings(
            expected_message)

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        envelope = ebxml_request_envelope.EbxmlRequestEnvelope(get_test_message_dictionary())

        message_id, http_headers, message = envelope.serialize()

        normalized_message = file_utilities.FileUtilities.normalize_line_endings(message)

        self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
        self.assertEqual(EXPECTED_HTTP_HEADERS, http_headers)
        self.assertEqual(self.normalized_expected_serialized_message, normalized_message)

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize_message_id_not_generated(self, mock_get_uuid, mock_get_timestamp):
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        message_dictionary = get_test_message_dictionary()
        message_dictionary[ebxml_envelope.MESSAGE_ID] = test_ebxml_envelope.MOCK_UUID
        envelope = ebxml_request_envelope.EbxmlRequestEnvelope(message_dictionary)

        message_id, http_headers, message = envelope.serialize()

        normalized_message = file_utilities.FileUtilities.normalize_line_endings(message)

        mock_get_uuid.assert_not_called()
        self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
        self.assertEqual(EXPECTED_HTTP_HEADERS, http_headers)
        self.assertEqual(self.normalized_expected_serialized_message, normalized_message)

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize_required_tags(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        for required_tag in get_test_message_dictionary().keys():
            with self.subTest(required_tag=required_tag):
                test_message_dict = get_test_message_dictionary()
                del test_message_dict[required_tag]
                envelope = ebxml_request_envelope.EbxmlRequestEnvelope(test_message_dict)

                with self.assertRaisesRegex(pystache_message_builder.MessageGenerationError, 'Failed to find key'):
                    envelope.serialize()

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize_optional_tags(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        test_cases = [
            (ebxml_request_envelope.DUPLICATE_ELIMINATION, 'eb:DuplicateElimination'),
            (ebxml_request_envelope.ACK_REQUESTED, 'eb:AckRequested'),
            (ebxml_request_envelope.SYNC_REPLY, 'eb:SyncReply')
        ]
        for optional_tag, optional_xml_tag in test_cases:
            with self.subTest(optional_tag=optional_tag):
                message_dictionary = get_test_message_dictionary()
                message_dictionary[optional_tag] = False
                envelope = ebxml_request_envelope.EbxmlRequestEnvelope(message_dictionary)

                message_id, http_headers, message = envelope.serialize()

                normalized_message = file_utilities.FileUtilities.normalize_line_endings(message)

                self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
                self.assertEqual(EXPECTED_HTTP_HEADERS, http_headers)
                self.assertNotEqual(self.normalized_expected_serialized_message, normalized_message)
                self.assertNotIn(optional_xml_tag, normalized_message)

    def test_from_string(self):
        with self.subTest("A valid request containing a payload"):
            message = file_utilities.FileUtilities.get_file_string(str(self.message_dir / "ebxml_request.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest("An invalid multi-part MIME message"):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / "ebxml_request_no_header.msg"))

            with self.assertRaises(ebxml_envelope.EbXmlParsingError):
                ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

        with self.subTest("A multi-part MIME message with a defect in the payload"):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / "ebxml_request_payload_defect.msg"))

            expected_values_with_test_payload = expected_values("mock-payload")

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_test_payload, parsed_message.message_dictionary)

        with self.subTest("A valid request that does not contain the optional payload MIME part"):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / "ebxml_request_no_payload.msg"))
            expected_values_with_no_payload = expected_values()

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_no_payload, parsed_message.message_dictionary)

        with self.subTest("A valid request containing an additional MIME part"):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / "ebxml_request_additional_attachment.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest("A message that is not a multi-part MIME message"):
            with self.assertRaises(ebxml_envelope.EbXmlParsingError):
                ebxml_request_envelope.EbxmlRequestEnvelope.from_string({CONTENT_TYPE_HEADER_NAME: "text/plain"},
                                                                        "A message")

    def test_from_string_missing_additional_values(self):
        sub_tests = [
            ('DuplicateElimination', 'ebxml_request_no_duplicate_elimination.msg',
             ebxml_request_envelope.DUPLICATE_ELIMINATION),
            ('SyncReply', 'ebxml_request_no_sync_reply.msg', ebxml_request_envelope.SYNC_REPLY)
        ]
        for element_name, filename, key in sub_tests:
            with self.subTest(f'A valid request without a {element_name} element'):
                message = file_utilities.FileUtilities.get_file_string(
                    str(self.message_dir / filename))
                expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)
                expected_values_with_payload[key] = False

                parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

                self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest(f'A valid request without an AckRequested element'):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / 'ebxml_request_no_ack_requested.msg'))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)
            expected_values_with_payload[ebxml_request_envelope.ACK_REQUESTED] = False
            del expected_values_with_payload[ebxml_request_envelope.ACK_SOAP_ACTOR]

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest(f'A valid request without an AckRequested SOAP actor attribute'):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / 'ebxml_request_no_soap_actor.msg'))

            with self.assertRaisesRegex(
                    ebxml_envelope.EbXmlParsingError, "Weren't able to find required attribute actor"):
                ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)
