from unittest.mock import patch

import mhs.common.messages.ebxml_ack_envelope as ebxml_ack_envelope
import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.tests.test_ebxml_envelope as test_ebxml_envelope
from builder import pystache_message_builder
from utilities import file_utilities
from utilities import message_utilities
from utilities import xml_utilities

EXPECTED_EBXML = "ebxml_ack.xml"
EXPECTED_VALUES = test_ebxml_envelope.BASE_EXPECTED_VALUES


def get_test_message_dictionary():
    return {
        ebxml_envelope.FROM_PARTY_ID: "TESTGEN-201324",
        ebxml_envelope.TO_PARTY_ID: "YEA-0000806",
        ebxml_envelope.CPA_ID: "S1001A1630",
        ebxml_envelope.CONVERSATION_ID: "79F49A34-9798-404C-AEC4-FD38DD81C138",
        ebxml_ack_envelope.RECEIVED_MESSAGE_TIMESTAMP: "2013-04-16T07:52:09Z",
        ebxml_envelope.RECEIVED_MESSAGE_ID: "0CDBA95F-74DA-47E9-8383-7B8E9167D146",
    }


class TestEbXmlAckEnvelope(test_ebxml_envelope.TestEbxmlEnvelope):

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP
        expected_message = file_utilities.FileUtilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))

        envelope = ebxml_ack_envelope.EbxmlAckEnvelope(get_test_message_dictionary())

        message_id, message = envelope.serialize()

        expected_message_bytes = expected_message.encode()
        message_bytes = message.encode()

        self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
        xml_utilities.XmlUtilities.assert_xml_equal(expected_message_bytes, message_bytes)

    @patch.object(message_utilities.MessageUtilities, "get_timestamp")
    @patch.object(message_utilities.MessageUtilities, "get_uuid")
    def test_serialize_required_tags(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP

        for required_tag in get_test_message_dictionary().keys():
            with self.subTest(required_tag=required_tag):
                test_message_dict = get_test_message_dictionary()
                del test_message_dict[required_tag]
                envelope = ebxml_ack_envelope.EbxmlAckEnvelope(test_message_dict)

                with self.assertRaisesRegex(pystache_message_builder.MessageGenerationError, 'Failed to find key'):
                    envelope.serialize()

    def test_from_string(self):
        message = file_utilities.FileUtilities.get_file_string(str(self.message_dir / "ebxml_header.xml"))

        parsed_message = ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, message)

        self.assertEqual(EXPECTED_VALUES, parsed_message.message_dictionary)

    def test_from_string_with_no_values(self):
        message = file_utilities.FileUtilities.get_file_string(str(self.message_dir / "ebxml_header_empty.xml"))

        with self.assertRaisesRegex(ebxml_envelope.EbXmlParsingError, "Weren't able to find required element"):
            ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, message)
