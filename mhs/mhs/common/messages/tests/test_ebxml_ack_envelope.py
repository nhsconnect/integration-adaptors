from unittest.mock import patch

from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities
from utilities.xml_utilities import XmlUtilities

import mhs.common.messages.ebxml_ack_envelope as ebxml_ack_envelope
import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.tests.test_ebxml_envelope as test_ebxml_envelope

EXPECTED_EBXML = "ebxml_ack.xml"


class TestEbXmlAckEnvelope(test_ebxml_envelope.TestEbxmlEnvelope):

    @patch.object(MessageUtilities, "get_timestamp")
    @patch.object(MessageUtilities, "get_uuid")
    def test_build_message(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = test_ebxml_envelope.MOCK_UUID
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

        self.assertEqual(test_ebxml_envelope.MOCK_UUID, message_id)
        XmlUtilities.assert_xml_equal(expected_message_bytes, message_bytes)

    def test_from_string(self):
        message = FileUtilities.get_file_string(str(self.message_dir / "ebxml_header.xml"))

        parsed_message = ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, message)

        self.assertEqual(test_ebxml_envelope.EXPECTED_VALUES, parsed_message.message_dictionary)

    def test_from_string_with_no_values(self):
        message = FileUtilities.get_file_string(str(self.message_dir / "ebxml_header_empty.xml"))

        parsed_message = ebxml_ack_envelope.EbxmlAckEnvelope.from_string({}, message)

        self.assertEqual({}, parsed_message.message_dictionary)
