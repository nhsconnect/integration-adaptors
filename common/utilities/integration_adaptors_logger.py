import contextvars
import datetime as dt
import logging
import sys
import traceback

from utilities import config

AUDIT = 25

message_id: contextvars.ContextVar[str] = contextvars.ContextVar('message_id', default=None)
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default=None)
inbound_message_id: contextvars.ContextVar[str] = contextvars.ContextVar('inbound_message_id', default=None)
interaction_id: contextvars.ContextVar[str] = contextvars.ContextVar('interaction_id', default=None)

def _check_for_insecure_log_level(log_level: str):
    integer_level = logging.getLevelName(log_level)
    if integer_level < logging.INFO:
        logger = IntegrationAdaptorsLogger('INSECURE-LOG-LEVEL')
        logger.critical('000',
                        'The current log level ({logLevel}) is set below INFO level, it is known that libraries used '
                        'by this application sometimes log out clinical patient data at DEBUG level. '
                        'The log level provided MUST NOT be used in a production environment.',
                        {'logLevel': log_level})


# Set the logging info globally, make each module get a new logger based on that log ref we provide
def configure_logging():
    """
    A general method to load the overall config of the system, specifically it modifies the root handler to output
    to stdout and sets the default log levels and format. This is expected to be called once at the start of a
    application.
    """

    class _CustomFormatter(logging.Formatter):
        """
        A private formatter class, this is required to provide microsecond precision timestamps and utc
        conversion
        """
        converter = dt.datetime.utcfromtimestamp

        def formatTime(self, record, datefmt):
            ct = self.converter(record.created)
            return ct.strftime(datefmt)

    logging.addLevelName(AUDIT, "AUDIT")
    logger = logging.getLogger()
    log_level = config.get_config('LOG_LEVEL')
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)

    formatter = _CustomFormatter(
        fmt='[%(asctime)sZ] %(message)s pid=%(process)d LogLevel=%(levelname)s LoggerName=%(name)s',
        datefmt='%Y-%m-%dT%H:%M:%S.%f')

    handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(handler)

    _check_for_insecure_log_level(log_level)


class IntegrationAdaptorsLogger(object):
    """
    To log exceptions correctly, key them with 'exception'
    """

    def __init__(self, log_ref: str):
        """
        :param log_ref: Used as part of the process key, this is a base log code to identify which module
        each log originates from
        """
        if not log_ref:
            raise ValueError('Undefined log reference')
        self.process_key_tag = log_ref
        self.logger = logging.getLogger(log_ref)

    def _format_and_write(self, message, values, process_key_num, level):
        """
        Formats the string and appends the appropriate values if they are included before writing the log
        """
        if not process_key_num:
            raise ValueError('process_key_num not defined')

        message = self._formatted_string(message, values)

        if message_id.get():
            message += f' RequestId={message_id.get()}'
        if correlation_id.get():
            message += f' CorrelationId={correlation_id.get()}'
        if inbound_message_id.get():
            message += f' InboundMessageId={inbound_message_id.get()}'
        if interaction_id.get():
            message += f' InteractionId={interaction_id.get()}'

        message += f' ProcessKey={self.process_key_tag + process_key_num}'

        self.logger.log(level, message)

    def info(self, process_key_num: str, message: str, values: dict = None):
        values = values if values is not None else {}
        self._format_and_write(message, values, process_key_num, logging.INFO)

    def audit(self, process_key_num: str, message: str, values: dict = None):
        values = values if values is not None else {}
        self._format_and_write(message, values, process_key_num, AUDIT)

    def warning(self, process_key_num: str, message: str, values: dict = None):
        values = values if values is not None else {}
        self._format_and_write(message, values, process_key_num, logging.WARNING)

    def error(self, process_key_num: str, message: str, values: dict = None):
        values = values if values is not None else {}
        self._format_and_write(message, values, process_key_num, logging.ERROR)

    def critical(self, process_key_num: str, message: str, values: dict = None):
        values = values if values is not None else {}
        self._format_and_write(message, values, process_key_num, logging.CRITICAL)

    def _format_values_in_map(self, dict_values: dict) -> dict:
        """
        Replaces the values in the map with key=value so that the key in a string can be replaced with the correct
        log format, also surrounds the value with quotes if it contains spaces and removes spaces from the key
        """

        for key in dict_values.keys():
            if str(key).lower() == "exception":
                dict_values[key] = self._format_exception(str(dict_values[key]))
                break

        new_map = {}
        for key, value in dict_values.items():
            value = str(value)
            if ' ' in value:
                value = f'"{value}"'

            new_map[key] = f"{key.replace(' ', '')}={value}"
        return new_map

    def _formatted_string(self, message: str, dict_values: dict) -> str:
        """
        Populates the string with the correctly formatted dictionary values
        """
        formatted_values = self._format_values_in_map(dict_values)
        return message.format(**formatted_values)

    @staticmethod
    def _format_exception(message: str) -> str:
        """
        Returns a formatted string of the last exception on the stack
        """
        exc_inf = sys.exc_info()
        if all(exc_inf):
            (etype, value, trace) = exc_inf
            if message:
                return f'{message}, {traceback.format_exception(etype, value, trace)}'
            else:
                return f'{traceback.format_exception(etype, value, trace)}'
