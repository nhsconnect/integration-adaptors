import copy
from unittest.mock import patch

from mhs_common.messages import ebxml_ack_envelope
from mhs_common.messages import common_ack_envelope
from mhs_common.messages import ebxml_envelope
from mhs_common.messages.tests import test_ebxml_envelope
from builder import pystache_message_builder
from utilities import file_utilities
from utilities import message_utilities
from utilities import xml_utilities

EXPECTED_EBXML = "ebxml_ack.xml"

EXPECTED_VALUES = copy.deepcopy(test_ebxml_envelope.BASE_EXPECTED_VALUES)
EXPECTED_VALUES[common_ack_envelope.RECEIVED_MESSAGE_TIMESTAMP] = EXPECTED_VALUES.pop(ebxml_envelope.TIMESTAMP)
EXPECTED_VALUES[ebxml_envelope.SERVICE] = 'urn:oasis:names:tc:ebxml-msg:service'
EXPECTED_VALUES[ebxml_envelope.ACTION] = 'Acknowledgment'


def get_test_message_dictionary():
    return {
        ebxml_envelope.FROM_PARTY_ID: "TESTGEN-201324",
        ebxml_envelope.TO_PARTY_ID: "YEA-0000806",
        ebxml_envelope.CPA_ID: "S1001A1630",
        ebxml_envelope.CONVERSATION_ID: "79F49A34-9798-404C-AEC4-FD38DD81C138",
        common_ack_envelope.RECEIVED_MESSAGE_TIMESTAMP: "2013-04-16T07:52:09Z",
        ebxml_envelope.RECEIVED_MESSAGE_ID: "0CDBA95F-74DA-47E9-8383-7B8E9167D146",
    }


class TestEbXmlAckEnvelope(test_ebxml_envelope.BaseTestEbxmlEnvelope):

    @patch.object(message_utilities, "get_timestamp")
    @patch.object(message_utilities, "get_uuid")
    def test_serialize(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP
        expected_message = file_utilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))
        expected_http_headers = {
            'charset': 'UTF-8', 'SOAPAction': 'urn:oasis:names:tc:ebxml-msg:service/Acknowledgment',
            'Content-Type': 'text/xml'
        }

        envelope = ebxml_ack_envelope.EbxmlAckEnvelope(get_test_message_dictionary())

        message_id, http_headers, message = envelope.serialize()

        expected_message_bytes = expected_message.encode()
        message_bytes = message.encode()

        self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
        self.assertEqual(expected_http_headers, http_headers)
        xml_utilities.XmlUtilities.assert_xml_equal(expected_message_bytes, message_bytes)

    @patch.object(message_utilities, "get_timestamp")
    @patch.object(message_utilities, "get_uuid")
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
        message = file_utilities.get_file_string(str(self.message_dir / "ebxml_header.xml"))

        parsed_message = ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, message)

        self.assertEqual(EXPECTED_VALUES, parsed_message.message_dictionary)

    def test_from_string_with_no_values(self):
        message = file_utilities.get_file_string(str(self.message_dir / "ebxml_header_empty.xml"))

        with self.assertRaisesRegex(ebxml_envelope.EbXmlParsingError, "Weren't able to find required element"):
            ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, message)

    @patch.object(message_utilities, "get_timestamp")
    @patch.object(message_utilities, "get_uuid")
    def test_roundtrip(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
        mock_get_timestamp.return_value = test_ebxml_envelope.MOCK_TIMESTAMP
        test_message_dict = get_test_message_dictionary()

        envelope = ebxml_ack_envelope.EbxmlAckEnvelope(test_message_dict)

        first_message_id, _, first_message = envelope.serialize()

        parsed_message = ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, first_message)

        second_message_id, _, second_message = parsed_message.serialize()

        self.assertEqual(first_message_id, second_message_id)
        self.assertEqual(second_message, first_message)
