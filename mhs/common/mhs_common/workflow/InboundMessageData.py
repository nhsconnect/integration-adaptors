from dataclasses import dataclass
from typing import List


@dataclass
class InboundMessageData:
    ebxml: str
    payload: str
    attachments: List
