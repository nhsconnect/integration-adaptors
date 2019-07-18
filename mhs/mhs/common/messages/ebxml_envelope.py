"""This module defines the envelope used to wrap asynchronous messages to be sent to a remote MHS."""

import mhs.common.messages.envelope as envelope


class EbxmlEnvelope(envelope.Envelope):
    """An envelope that contains a message to be sent asynchronously to a remote MHS."""
    pass
