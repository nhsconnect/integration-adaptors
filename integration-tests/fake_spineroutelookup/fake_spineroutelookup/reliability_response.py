from __future__ import annotations


class ReliabilityResponse(object):

    def __init__(self):
        self.sync_reply_mode = "MSHSignalsOnly"
        self.retries = "3"
        self.persist_duration = "PT5M"
        self.ack_requested = "MSHSignalsOnly"
        self.duplicate_elimination = "always"
        self.retry_interval = "PT0.5S"  # 0.5 seconds

    def override_sync_reply_mode(self, reply_mode: str) -> ReliabilityResponse:
        self.sync_reply_mode = reply_mode
        return self

    def override_retries(self, retries: str) -> ReliabilityResponse:
        self.retries = retries
        return self

    def override_persist_duration(self, persist_duration) -> ReliabilityResponse:
        self.persist_duration = persist_duration
        return self

    def override_ack_requested(self, ack_requested) -> ReliabilityResponse:
        self.ack_requested = ack_requested
        return self

    def override_duplicate_elimination(self, duplicate_elimination) -> ReliabilityResponse:
        self.duplicate_elimination = duplicate_elimination
        return self

    def override_retry_interval(self, retry_interval) -> ReliabilityResponse:
        self.retry_interval = retry_interval
        return self

    def get_response(self) -> dict:
        return {
            "nhsMHSSyncReplyMode": self.sync_reply_mode,
            "nhsMHSRetries": self.retries,
            "nhsMHSPersistDuration": self.persist_duration,
            "nhsMHSAckRequested": self.ack_requested,
            "nhsMHSDuplicateElimination": self.duplicate_elimination,
            "nhsMHSRetryInterval": self.retry_interval
        }
