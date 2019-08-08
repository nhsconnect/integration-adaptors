"""This module defines the envelope used to wrap synchronous messages to be sent to a remote MHS."""

import messages.envelope as envelope


class SoapEnvelope(envelope.Envelope):
    """An envelope that contains a message to be sent synchronously to a remote MHS."""
    pass
