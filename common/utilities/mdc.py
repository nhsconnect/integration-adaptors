import contextvars

from comms.http_headers import HttpHeaders

message_id: contextvars.ContextVar[str] = contextvars.ContextVar('message_id', default='')
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default='')
inbound_message_id: contextvars.ContextVar[str] = contextvars.ContextVar('inbound_message_id', default='')
interaction_id: contextvars.ContextVar[str] = contextvars.ContextVar('interaction_id', default='')


def build_tracking_headers():
    headers = {}
    if correlation_id.get():
        headers[HttpHeaders.CORRELATION_ID] = correlation_id.get()
    if message_id.get():
        headers[HttpHeaders.MESSAGE_ID] = message_id.get()
    if interaction_id.get():
        headers[HttpHeaders.INTERACTION_ID] = interaction_id.get()
    if inbound_message_id.get():
        headers[HttpHeaders.INBOUND_MESSAGE_ID] = inbound_message_id.get()
    return headers or None
