import os
from pathlib import Path
from unittest import TestCase

from utilities.fileutilities import FileUtilities

from mhs.builder.ebxmlmessagebuilder import EbXmlMessageBuilder

EXPECTED_MESSAGES_DIR = "expected_messages"
EXPECTED_EBXML = "ebxml.xml"


class TestEbXmlMessageBuilder(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_message_dir = Path(current_dir) / EXPECTED_MESSAGES_DIR

    def setUp(self):
        self.builder = EbXmlMessageBuilder()

    def test_build_message(self):
        expected_message = FileUtilities.get_file_string(str(self.expected_message_dir / EXPECTED_EBXML))

        message = self.builder.build_message({
            "from_party_id": "TESTGEN-201324",
            "to_party_id": "YEA-0000806",
            "cpa_id": "S1001A1630",
            "conversation_id": "54DE3828-6062-11E9-A444-0050562EB96B",
            "message_GUID": "54DE3828-6062-11E9-A444-0050562EB96B",
            "service": "urn:nhs:names:services:pdsquery",
            "action": "QUPA_IN000006UK02",
            "timestamp": "2012-03-15T06:51:08Z",
            "duplicate_elimination": True,
            "ack_requested": True,
            "ack_soap_actor": "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
            "sync_reply": True,
            "hl7_message": '<QUPA_IN000006UK02 xmlns="urn:hl7-org:v3"></QUPA_IN000006UK02>'
        })

        self.assertEqual(expected_message, message)
