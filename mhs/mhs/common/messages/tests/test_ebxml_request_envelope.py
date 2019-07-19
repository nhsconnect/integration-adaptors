import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from utilities.file_utilities import FileUtilities
from utilities.message_utilities import MessageUtilities

import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.ebxml_request_envelope as ebxml_request_envelope

EXPECTED_MESSAGES_DIR = "expected_messages"
EXPECTED_EBXML = "ebxml_request.xml"

MOCK_UUID = "5BB171D4-53B2-4986-90CF-428BE6D157F5"


class TestEbxmlRequestEnvelope(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_message_dir = Path(current_dir) / EXPECTED_MESSAGES_DIR

    def setUp(self):
        self.envelope = ebxml_request_envelope.EbxmlRequestEnvelope({
            ebxml_envelope.FROM_PARTY_ID: "TESTGEN-201324",
            ebxml_envelope.TO_PARTY_ID: "YEA-0000806",
            ebxml_envelope.CPA_ID: "S1001A1630",
            ebxml_envelope.CONVERSATION_ID: "79F49A34-9798-404C-AEC4-FD38DD81C138",
            ebxml_request_envelope.SERVICE: "urn:nhs:names:services:pdsquery",
            ebxml_request_envelope.ACTION: "QUPA_IN000006UK02",
            ebxml_request_envelope.DUPLICATE_ELIMINATION: True,
            ebxml_request_envelope.ACK_REQUESTED: True,
            ebxml_request_envelope.ACK_SOAP_ACTOR: "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
            ebxml_request_envelope.SYNC_REPLY: True,
            ebxml_request_envelope.MESSAGE: '<QUPA_IN000006UK02 xmlns="urn:hl7-org:v3"></QUPA_IN000006UK02>'
        })

    @patch.object(MessageUtilities, "get_timestamp")
    @patch.object(MessageUtilities, "get_uuid")
    def test_build_message(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = MOCK_UUID
        mock_get_timestamp.return_value = "2012-03-15T06:51:08Z"
        expected_message = FileUtilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))

        message_id, message = self.envelope.serialize()

        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of both strings
        normalized_expected_message = FileUtilities.normalize_line_endings(expected_message)
        normalized_message = FileUtilities.normalize_line_endings(message)

        self.assertEqual(MOCK_UUID, message_id)
        self.assertEqual(normalized_expected_message, normalized_message)
