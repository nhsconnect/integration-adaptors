from http_constants import headers


class HttpHeaders(headers.HttpHeaders):
    CORRELATION_ID = "Correlation-Id"
    MESSAGE_ID = "Message-Id"
    INTERACTION_ID = "Interaction-Id"
    INBOUND_MESSAGE_ID = "Inbound-Message-Id"
    FROM_ASID = "from-asid"
    SYNC_ASYNC = "sync-async"
    ODS_CODE = "ods-code"
