import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from mhs.builder.ebxml_ack_message_builder import EbXmlAckMessageBuilder, RECEIVED_MESSAGE_TIMESTAMP, \
    RECEIVED_MESSAGE_ID
from mhs.builder.ebxml_message_builder import FROM_PARTY_ID, TO_PARTY_ID, CPA_ID, CONVERSATION_ID
from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities

EXPECTED_MESSAGES_DIR = "expected_messages"
EXPECTED_EBXML = "ebxml_ack.xml"


class TestEbXmlAckMessageBuilder(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_message_dir = Path(current_dir) / EXPECTED_MESSAGES_DIR

    def setUp(self):
        self.builder = EbXmlAckMessageBuilder()

    @patch.object(MessageUtilities, "get_timestamp")
    @patch.object(MessageUtilities, "get_uuid")
    def test_build_message(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = "5BB171D4-53B2-4986-90CF-428BE6D157F5"
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_message = FileUtilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))

        message = self.builder.build_message({
            FROM_PARTY_ID: "TESTGEN-201324",
            TO_PARTY_ID: "YEA-0000806",
            CPA_ID: "S1001A1630",
            CONVERSATION_ID: "79F49A34-9798-404C-AEC4-FD38DD81C138",
            RECEIVED_MESSAGE_TIMESTAMP: "2013-04-16T07:52:09Z",
            RECEIVED_MESSAGE_ID: "0CDBA95F-74DA-47E9-8383-7B8E9167D146",
        })

        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of both strings
        normalized_expected_message = FileUtilities.normalize_line_endings(expected_message)
        normalized_message = FileUtilities.normalize_line_endings(message)

        self.assertEqual(normalized_expected_message, normalized_message)
