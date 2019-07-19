"""This module defines the envelope used to wrap asynchronous request messages to be sent to a remote MHS."""
import typing

import mhs.common.messages.ebxml_envelope as ebxml_envelope

EBXML_TEMPLATE = "ebxml_request"

SERVICE = "service"
ACTION = "action"
DUPLICATE_ELIMINATION = "duplicate_elimination"
ACK_REQUESTED = "ack_requested"
ACK_SOAP_ACTOR = "ack_soap_actor"
SYNC_REPLY = "sync_reply"
MESSAGE = "hl7_message"


class EbxmlRequestEnvelope(ebxml_envelope.EbxmlEnvelope):
    """An envelope that contains a request to be sent asynchronously to a remote MHS."""

    def __init__(self, message_dictionary: typing.Dict[str, str]):
        """Create a new EbxmlRequestEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        super().__init__(EBXML_TEMPLATE, message_dictionary)
