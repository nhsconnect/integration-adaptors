import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from mhs.builder.ebxml_request_message_builder import EbXmlRequestMessageBuilder
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
            "from_party_id": "TESTGEN-201324",
            "to_party_id": "YEA-0000806",
            "cpa_id": "S1001A1630",
            "service": "urn:nhs:names:services:pdsquery",
            "action": "QUPA_IN000006UK02",
            "duplicate_elimination": True,
            "ack_requested": True,
            "ack_soap_actor": "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
            "sync_reply": True,
            "hl7_message": '<QUPA_IN000006UK02 xmlns="urn:hl7-org:v3"></QUPA_IN000006UK02>'
        })

        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of both strings
        normalized_expected_message = FileUtilities.normalize_line_endings(expected_message)
        normalized_message = FileUtilities.normalize_line_endings(message)

        self.assertEqual(normalized_expected_message, normalized_message)
