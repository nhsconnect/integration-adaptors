import datetime
import inspect
import time
from functools import wraps

import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


class Stopwatch(object):

    start_time = None

    def start_timer(self):
        self.start_time = time.perf_counter()

    def stop_timer(self):
        end_time = time.perf_counter()
        diff = end_time - self.start_time
        return diff


def _begin_stopwatch():
    stopwatch = Stopwatch()
    stopwatch.start_timer()
    return stopwatch


def _log_time(duration, func_name):
    duration = round(duration, 3)
    logger.info('{FuncName} took {Duration} seconds', fparams={'FuncName': func_name, 'Duration': duration})


def _log_tornado_time(duration, handler, func_name):
    duration = round(duration, 3)
    logger.info('{FuncName} from {Handler} took {Duration} seconds',
                fparams={'FuncName': func_name, 'Handler': handler, 'Duration': duration})


def time_function(func):
    """
    A method decorator that logs the time taken to execute a given method
    """

    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def invoke_method_with_timer(*args, **kwargs):
            stopwatch = _begin_stopwatch()
            try:
                return await func(*args, **kwargs)
            finally:
                _log_time(stopwatch.stop_timer(), func.__name__)
    else:
        @wraps(func)
        def invoke_method_with_timer(*args, **kwargs):
            stopwatch = _begin_stopwatch()
            try:
                return func(*args, **kwargs)
            finally:
                _log_time(stopwatch.stop_timer(), func.__name__)

    return invoke_method_with_timer


def time_request(func):
    """
    A method to be used with tornado end points to extract their calling details and time their execution, this
    mainly holds as a placeholder if any extra data is required from the call
    """
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def method_wrapper(*args, **kwargs):
            handler = args[0]
            stopwatch = _begin_stopwatch()

            try:
                return await func(*args, **kwargs)
            finally:
                _log_tornado_time(stopwatch.stop_timer(),
                                  handler.__class__.__name__,
                                  handler.request.method.lower())

        return method_wrapper
    else:
        @wraps(func)
        def method_wrapper(*args, **kwargs):
            handler = args[0]
            stopwatch = _begin_stopwatch()

            try:
                return func(*args, **kwargs)
            finally:
                _log_tornado_time(stopwatch.stop_timer(),
                                  handler.__class__.__name__,
                                  handler.request.method.lower())

    return method_wrapper


def get_time() -> str:
    """Returns UTC time in the appropriate format """
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
