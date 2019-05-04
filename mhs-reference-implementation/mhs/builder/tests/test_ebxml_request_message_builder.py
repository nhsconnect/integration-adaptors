import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from mhs.builder.ebxml_message_builder import FROM_PARTY_ID, TO_PARTY_ID, CPA_ID, CONVERSATION_ID
from mhs.builder.ebxml_request_message_builder import EbXmlRequestMessageBuilder, MESSAGE, SERVICE, ACTION, \
    DUPLICATE_ELIMINATION, ACK_REQUESTED, ACK_SOAP_ACTOR, SYNC_REPLY
from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities

EXPECTED_MESSAGES_DIR = "expected_messages"
EXPECTED_EBXML = "ebxml_request.xml"


class TestEbXmlRequestMessageBuilder(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_message_dir = Path(current_dir) / EXPECTED_MESSAGES_DIR

    def setUp(self):
        self.builder = EbXmlRequestMessageBuilder()

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
            SERVICE: "urn:nhs:names:services:pdsquery",
            ACTION: "QUPA_IN000006UK02",
            DUPLICATE_ELIMINATION: True,
            ACK_REQUESTED: True,
            ACK_SOAP_ACTOR: "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
            SYNC_REPLY: True,
            MESSAGE: '<QUPA_IN000006UK02 xmlns="urn:hl7-org:v3"></QUPA_IN000006UK02>'
        })

        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of both strings
        normalized_expected_message = FileUtilities.normalize_line_endings(expected_message)
        normalized_message = FileUtilities.normalize_line_endings(message)

        self.assertEqual(normalized_expected_message, normalized_message)
