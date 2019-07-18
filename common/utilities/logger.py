import logging
import sys
import time

# Set a custom log level
AUDIT = 25
logging.addLevelName(AUDIT, "AUDIT")


def audit(self, message, *args, **kws):
    if self.isEnabledFor(AUDIT):
        self._log(AUDIT, message, args, **kws)


logging.Logger.audit = audit


def load_global_log_config():
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.NOTSET)
    logging.Formatter.converter = time.gmtime
    formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] '
                                  '%(message)s pid=%(process)d LogLevel=%(levelname)s ProcessKey=%(processKey)s',
                                  '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _format_values_in_map(dict_values: dict) -> dict:
    new_map = {}
    for key, value in dict_values.items():
        if ' ' in value:
            value = f"\"{value}\""

        new_map[key] = f"{key.replace(' ', '')}={value}"
    return new_map


def _formatted_string(message: str, dict_values: dict) -> str:
    formatted_values = _format_values_in_map(dict_values)
    return message.format(**formatted_values)


class Logger:

    def __init__(self, log_ref: str = "SYS"):
        self.process_key_tag = log_ref
        self.logger = logging.getLogger()

    def _write(self, level, message, process_key_num: str):
        if not process_key_num:
            process_key_num = "000"
        self.logger.log(level, message, extra={'processKey': self.process_key_tag + process_key_num})

    def _format_and_write(self, message, values, process_key_num, request_id, correlation_id, level):
        message = _formatted_string(message, values)

        if request_id:
            message += f' RequestId={request_id}'
        if correlation_id:
            message += f' CorrelationId={correlation_id}'

        self._write(level, message, process_key_num)

    def info(self, message: str, values: dict = None, process_key_num: str = None,
             request_id: str = None, correlation_id=None):
        if values is None:
            values = {}
        self._format_and_write(message, values, process_key_num, request_id, correlation_id, logging.INFO)

    def audit(self, message: str, values: dict = None, process_key_num: str = None,
              request_id: str = None, correlation_id=None):
        if values is None:
            values = {}
        self._format_and_write(message, values, process_key_num, request_id, correlation_id, AUDIT)

    def warning(self, message: str, values: dict = None, process_key_num: str = None,
                request_id: str = None, correlation_id=None):
        if values is None:
            values = {}
        self._format_and_write(message, values, process_key_num, request_id, correlation_id, logging.WARNING)

    def error(self, message: str, values: dict = None, process_key_num: str = None,
              request_id: str = None, correlation_id=None):
        if values is None:
            values = {}
        self._format_and_write(message, values, process_key_num, request_id, correlation_id, logging.ERROR)

    def critical(self, message: str, values: dict = None, process_key_num: str = None,
                 request_id: str = None, correlation_id=None):
        if values is None:
            values = {}
        self._format_and_write(message, values, process_key_num, request_id, correlation_id, logging.CRITICAL)
