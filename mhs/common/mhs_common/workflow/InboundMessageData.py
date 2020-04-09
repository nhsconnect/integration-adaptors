from typing import List


class InboundMessageData:
    def __init__(self, soap_message: str, payload: str, attachments: List):
        self.ebXML = soap_message
        self.payload = payload
        self.attachments = attachments
