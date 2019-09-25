import copy
from unittest.mock import patch

from builder import pystache_message_builder
from utilities import file_utilities
from utilities import message_utilities

import mhs_common.messages.ebxml_envelope as ebxml_envelope
import mhs_common.messages.ebxml_request_envelope as ebxml_request_envelope
import mhs_common.messages.tests.test_ebxml_envelope as test_ebxml_envelope

EXPECTED_EBXML = "ebxml_request.xml"

CONTENT_TYPE_HEADER_NAME = "Content-Type"
MULTIPART_MIME_HEADERS = {CONTENT_TYPE_HEADER_NAME: 'multipart/related; boundary="--=_MIME-Boundary"'}
EXPECTED_MESSAGE = '<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>'

_ADDITIONAL_EXPECTED_VALUES = {
    ebxml_request_envelope.DUPLICATE_ELIMINATION: True,
    ebxml_request_envelope.ACK_REQUESTED: True,
    ebxml_request_envelope.ACK_SOAP_ACTOR: "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
    ebxml_request_envelope.SYNC_REPLY: True,
    ebxml_request_envelope.ATTACHMENTS: []
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
    values = copy.deepcopy(EXPECTED_VALUES)

    if message:
        values[ebxml_request_envelope.MESSAGE] = message

    return values


class TestEbxmlRequestEnvelope(test_ebxml_envelope.BaseTestEbxmlEnvelope):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.normalized_expected_serialized_message = self._get_expected_file_string(EXPECTED_EBXML)

    #####################
    # Serialisation tests
    #####################

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize_with_no_attachments(self, mock_get_uuid, mock_get_timestamp):
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
    def test_serialize_with_one_attachment(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.side_effect = ["8F1D7DE1-02AB-48D7-A797-A947B09F347F", test_ebxml_envelope.MOCK_UUID]
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        message_dictionary = get_test_message_dictionary()
        message_dictionary[ebxml_request_envelope.ATTACHMENTS] = [{
            ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
            ebxml_request_envelope.ATTACHMENT_BASE64: False,
            ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Some description',
            ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload'
        }]
        envelope = ebxml_request_envelope.EbxmlRequestEnvelope(message_dictionary)

        message_id, http_headers, message = envelope.serialize()

        normalized_expected_message = self._get_expected_file_string('ebxml_request_one_attachment.xml')
        normalized_message = file_utilities.FileUtilities.normalize_line_endings(message)

        self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
        self.assertEqual(EXPECTED_HTTP_HEADERS, http_headers)
        self.assertEqual(normalized_expected_message, normalized_message)

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize_with_multiple_attachments(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.side_effect = [
            "8F1D7DE1-02AB-48D7-A797-A947B09F347F", "64A73E03-30BD-4231-9959-0C4B54400345",
            test_ebxml_envelope.MOCK_UUID
        ]
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        message_dictionary = get_test_message_dictionary()
        message_dictionary[ebxml_request_envelope.ATTACHMENTS] = [
            {
                ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
                ebxml_request_envelope.ATTACHMENT_BASE64: False,
                ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Some description',
                ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload'
            },
            {
                ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'image/png',
                ebxml_request_envelope.ATTACHMENT_BASE64: True,
                ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Another description',
                ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'QW5vdGhlciBwYXlsb2Fk'
            }
        ]
        envelope = ebxml_request_envelope.EbxmlRequestEnvelope(message_dictionary)

        message_id, http_headers, message = envelope.serialize()

        normalized_expected_message = self._get_expected_file_string('ebxml_request_multiple_attachments.xml')
        normalized_message = file_utilities.FileUtilities.normalize_line_endings(message)

        self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
        self.assertEqual(EXPECTED_HTTP_HEADERS, http_headers)
        self.assertEqual(normalized_expected_message, normalized_message)

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
    def test_serialize_raises_error_when_required_tags_not_passed(self, mock_get_uuid, mock_get_timestamp):
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
    def test_serialize_raises_error_when_required_attachment_tags_not_passed(self, mock_get_uuid, mock_get_timestamp):
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        required_tags = [
            ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE, ebxml_request_envelope.ATTACHMENT_BASE64,
            ebxml_request_envelope.ATTACHMENT_DESCRIPTION, ebxml_request_envelope.ATTACHMENT_PAYLOAD
        ]
        for required_tag in required_tags:
            with self.subTest(required_tag=required_tag):
                mock_get_uuid.side_effect = ["8F1D7DE1-02AB-48D7-A797-A947B09F347F", test_ebxml_envelope.MOCK_UUID]

                message_dictionary = get_test_message_dictionary()
                message_dictionary[ebxml_request_envelope.ATTACHMENTS] = [{
                    ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
                    ebxml_request_envelope.ATTACHMENT_BASE64: False,
                    ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Some description',
                    ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload'
                }]
                del message_dictionary[ebxml_request_envelope.ATTACHMENTS][0][required_tag]
                envelope = ebxml_request_envelope.EbxmlRequestEnvelope(message_dictionary)

                with self.assertRaisesRegex(pystache_message_builder.MessageGenerationError, 'Failed to find key'):
                    envelope.serialize()

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize_doesnt_include_xml_tag_when_corresponding_boolean_flag_set_to_false(self, mock_get_uuid,
                                                                                           mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        test_cases = [
            (ebxml_request_envelope.DUPLICATE_ELIMINATION, 'eb:DuplicateElimination'),
            (ebxml_request_envelope.ACK_REQUESTED, 'eb:AckRequested'),
            (ebxml_request_envelope.SYNC_REPLY, 'eb:SyncReply')
        ]
        for boolean_tag, boolean_xml_tag in test_cases:
            with self.subTest(boolean_tag=boolean_tag):
                message_dictionary = get_test_message_dictionary()
                message_dictionary[boolean_tag] = False
                envelope = ebxml_request_envelope.EbxmlRequestEnvelope(message_dictionary)

                message_id, http_headers, message = envelope.serialize()

                normalized_message = file_utilities.FileUtilities.normalize_line_endings(message)

                self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
                self.assertEqual(EXPECTED_HTTP_HEADERS, http_headers)
                self.assertNotEqual(self.normalized_expected_serialized_message, normalized_message)
                self.assertNotIn(boolean_xml_tag, normalized_message)

    #######################
    # Deserialisation tests
    #######################

    def test_from_string_parses_valid_requests(self):
        with self.subTest("A valid request containing a payload"):
            message = file_utilities.FileUtilities.get_file_string(str(self.message_dir / "ebxml_request.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

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

        with self.subTest("A valid request containing one textual attachment"):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / "ebxml_request_one_attachment.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)
            expected_values_with_payload[ebxml_request_envelope.ATTACHMENTS].append({
                ebxml_request_envelope.ATTACHMENT_CONTENT_ID: '8F1D7DE1-02AB-48D7-A797-A947B09F347F@spine.nhs.uk',
                ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
                ebxml_request_envelope.ATTACHMENT_BASE64: False,
                ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Some description',
                ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload'
            })

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest("A valid request containing one textual attachment with application/xml content type"):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / "ebxml_request_one_attachment_application_xml_content_type.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)
            expected_values_with_payload[ebxml_request_envelope.ATTACHMENTS].append({
                ebxml_request_envelope.ATTACHMENT_CONTENT_ID: '8F1D7DE1-02AB-48D7-A797-A947B09F347F@spine.nhs.uk',
                ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
                ebxml_request_envelope.ATTACHMENT_BASE64: False,
                ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Some description',
                ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload'
            })

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest("A valid request containing one textual and one base64 attachment"):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / "ebxml_request_multiple_attachments.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)
            expected_values_with_payload[ebxml_request_envelope.ATTACHMENTS] += [
                {
                    ebxml_request_envelope.ATTACHMENT_CONTENT_ID: '8F1D7DE1-02AB-48D7-A797-A947B09F347F@spine.nhs.uk',
                    ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
                    ebxml_request_envelope.ATTACHMENT_BASE64: False,
                    ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Some description',
                    ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload'
                },
                {
                    ebxml_request_envelope.ATTACHMENT_CONTENT_ID: '64A73E03-30BD-4231-9959-0C4B54400345@spine.nhs.uk',
                    ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'image/png',
                    ebxml_request_envelope.ATTACHMENT_BASE64: True,
                    ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Another description',
                    ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR'
                                                               '42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
                }]

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

    def test_from_string_errors_on_invalid_request(self):
        with self.subTest("A message that is not a multi-part MIME message"):
            with self.assertRaises(ebxml_envelope.EbXmlParsingError):
                ebxml_request_envelope.EbxmlRequestEnvelope.from_string({CONTENT_TYPE_HEADER_NAME: "text/plain"},
                                                                        "A message")

        sub_tests = [
            ("An invalid multi-part MIME message", "ebxml_request_no_header.msg"),
            ("A message with an invalid binary ebXML header", "ebxml_request_invalid_binary_ebxml_header.msg"),
            ("A message with an invalid binary HL7 payload", "ebxml_request_invalid_binary_hl7_payload.msg"),
            ("A message with an invalid application/xml binary HL7 payload",
             "ebxml_request_invalid_application_xml_binary_hl7_payload.msg")
        ]
        for sub_test_name, filename in sub_tests:
            with self.subTest(sub_test_name):
                message = file_utilities.FileUtilities.get_file_string(
                    str(self.message_dir / filename))

                with self.assertRaises(ebxml_envelope.EbXmlParsingError):
                    ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

    def test_from_string_parses_messages_with_optional_parts_missing(self):
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

                parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS,
                                                                                         message)

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

        with self.subTest("A valid request containing one attachment without a description has description defaulted "
                          "to an empty string"):
            message = file_utilities.FileUtilities.get_file_string(
                str(self.message_dir / "ebxml_request_one_attachment_without_description.msg"))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)
            expected_values_with_payload[ebxml_request_envelope.ATTACHMENTS].append({
                ebxml_request_envelope.ATTACHMENT_CONTENT_ID: '8F1D7DE1-02AB-48D7-A797-A947B09F347F@spine.nhs.uk',
                ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
                ebxml_request_envelope.ATTACHMENT_BASE64: False,
                ebxml_request_envelope.ATTACHMENT_DESCRIPTION: '',
                ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload'
            })

            parsed_message = ebxml_request_envelope.EbxmlRequestEnvelope.from_string(MULTIPART_MIME_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

    #######################
    # Helper methods
    #######################

    def _get_expected_file_string(self, filename: str):
        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of the strings being compared
        return file_utilities.FileUtilities.normalize_line_endings(
            file_utilities.FileUtilities.get_file_string(str(self.expected_message_dir / filename)))
