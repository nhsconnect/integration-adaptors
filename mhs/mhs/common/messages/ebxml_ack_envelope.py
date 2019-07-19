"""This module defines the envelope used to wrap the acknowledgement messages to be sent to a remote MHS in response to
an asynchronous request."""
import typing

import mhs.common.messages.ebxml_envelope as ebxml_envelope

EBXML_TEMPLATE = "ebxml_ack"

RECEIVED_MESSAGE_TIMESTAMP = "received_message_timestamp"
RECEIVED_MESSAGE_ID = "received_message_id"


class EbxmlAckEnvelope(ebxml_envelope.EbxmlEnvelope):
    """An envelope that contains an acknowledgement of an asynchronous request from a remote MHS."""

    def __init__(self, message_dictionary: typing.Dict[str, str]):
        """Create a new EbxmlAckEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        super().__init__(EBXML_TEMPLATE, message_dictionary)
