"""A simple script to test the use of a PystacheMessageBuilder."""

from mhs.builder.pystachemessagebuilder import PystacheMessageBuilder

builder = PystacheMessageBuilder("templates", "ebxml")
message = builder.build_message({
    "from_party_id": "TESTGEN-201324",
    "to_party_id": "YEA-0000806",
    "cpa_id": "S1001A1630",
    "conversation_id": "54DE3828-6062-11E9-A444-0050562EB96B",
    "message_GUID": "54DE3828-6062-11E9-A444-0050562EB96B",
    "service": "urn:nhs:names:services:pdsquery",
    "action": "QUPA_IN000006UK02",
    "timestamp": "2012-03-15T06:51:08Z",
    "duplicate_elimination": False,
    "ack_requested": False,
    "ack_soap_actor": "urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
    "sync_reply": False,
    "hl7_message": '<QUPA_IN000006UK02 xmlns="urn:hl7-org:v3"></QUPA_IN000006UK02>'
})

print(message)
