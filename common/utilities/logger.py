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


def _format_values_in_map(dict_values: dict) -> dict:
    new_map = {}
    for key, value in dict_values.items():
        if ' ' in value:
            value = f"\"{value}\""

        new_map[key] = f"{key.replace(' ', '')}={value}"
    return new_map


def _append_additional_information(
        process_key: str = None,
        process_id: str = None,
        request_id: str = None,
        correlation_id: str = None):
    end_message = ''
    if process_key:
        end_message += f' ProcessKey={process_key}'
    if process_id:
        end_message += f' ProcessId={process_id}'
    if request_id:
        end_message += f' RequestId={request_id}'
    if correlation_id:
        end_message += f' CorrelationId={correlation_id}'

    return end_message


def _formatted_string(message: str, dict_values: dict) -> str:
    formatted_values = _format_values_in_map(dict_values)
    return message.format(**formatted_values)


class Logger:

    def __init__(self, log_file: str, log_level: int = logging.INFO):
        self.logger = logging.getLogger()

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        logging.Formatter.converter = time.gmtime
        formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s LogLevel=%(levelname)s',
                                      '%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(log_level)

    def _write(self, level, message):
        self.logger.log(level, message)

    def info(self, message, values,
             process_key: str = None,
             process_id: str = None,
             request_id: str = None,
             correlation_id=None):
        message = _formatted_string(message, values)
        message += _append_additional_information(process_key, process_id, request_id, correlation_id)
        self._write(logging.INFO, message)

    def audit(self, message, values,
              process_key: str = None,
              process_id: str = None,
              request_id: str = None,
              correlation_id=None):
        message = _formatted_string(message, values)
        message += _append_additional_information(process_key, process_id, request_id, correlation_id)
        self._write(AUDIT, message)

    def warning(self, message, values,
                process_key: str = None,
                process_id: str = None,
                request_id: str = None,
                correlation_id=None):
        message = _formatted_string(message, values)
        message += _append_additional_information(process_key, process_id, request_id, correlation_id)
        self._write(logging.WARNING, message)

    def error(self, message, values,
              process_key: str = None,
              process_id: str = None,
              request_id: str = None,
              correlation_id=None):
        message = _formatted_string(message, values)
        message += _append_additional_information(process_key, process_id, request_id, correlation_id)
        self._write(logging.ERROR, message)

    def critical(self, message, values,
                 process_key: str = None,
                 process_id: str = None,
                 request_id: str = None,
                 correlation_id=None):
        message = _formatted_string(message, values)
        message += _append_additional_information(process_key, process_id, request_id, correlation_id)
        self._write(logging.CRITICAL, message)
