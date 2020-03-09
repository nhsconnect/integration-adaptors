import contextvars
import datetime as dt
import logging
import sys
from logging import LogRecord
from typing import Optional

from utilities import config

AUDIT = 25

message_id: contextvars.ContextVar[str] = contextvars.ContextVar('message_id', default=None)
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default=None)
inbound_message_id: contextvars.ContextVar[str] = contextvars.ContextVar('inbound_message_id', default=None)
interaction_id: contextvars.ContextVar[str] = contextvars.ContextVar('interaction_id', default=None)


def _check_for_insecure_log_level(log_level: str):
    integer_level = logging.getLevelName(log_level)
    if integer_level < logging.INFO:
        logger = logging.getLogger(__name__)
        logger.critical('The current log level (%s) is set below INFO level, it is known that libraries used '
                        'by this application sometimes log out clinical patient data at DEBUG level. '
                        'The log level provided MUST NOT be used in a production environment.',
                        log_level)


class CustomFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            fmt='%(asctime)sZ | %(levelname)s | %(process)d | %(interaction_id)s | %(message_id)s | %(correlation_id)s | %(inbound_message_id)s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S.%f')

    def format(self, record: LogRecord) -> str:
        record.message_id = message_id.get() or ''
        record.correlation_id = correlation_id.get() or ''
        record.inbound_message_id = inbound_message_id.get() or ''
        record.interaction_id = interaction_id.get() or ''
        return super().format(record)

    def formatTime(self, record: LogRecord, datefmt: Optional[str] = ...) -> str:
        converter = dt.datetime.utcfromtimestamp
        ct = converter(record.created)
        s = ct.strftime(datefmt)
        return s


def configure_logging():
    """
    A general method to load the overall config of the system, specifically it modifies the root handler to output
    to stdout and sets the default log levels and format. This is expected to be called once at the start of a
    application.
    """
    logging.addLevelName(AUDIT, "AUDIT")
    logger = logging.getLogger()
    log_level = config.get_config('LOG_LEVEL')
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)

    formatter = CustomFormatter()

    handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(handler)

    def audit(self, message, *args, **kwargs):
        if self.isEnabledFor(AUDIT):
            self._log(AUDIT, message, args, **kwargs)
    logging.Logger.audit = audit

    _check_for_insecure_log_level(log_level)
