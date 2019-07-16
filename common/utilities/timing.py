import inspect
import logging
import time
from functools import wraps


class StopWatch:

    start_time = None

    def start_timer(self):
        self.start_time = time.perf_counter()

    def stop_timer(self):
        end_time = time.perf_counter()
        diff = end_time - self.start_time
        return diff


def _begin_stopwatch():
    stopwatch = StopWatch()
    stopwatch.start_timer()
    return stopwatch


def _log_time(duration, name):
    duration = round(duration, 3)
    logging.info(f'Method name={name} took duration={duration}')


def _log_tornado_time(duration, handler, method):
    duration = round(duration, 3)
    logging.info(f'method={method} from handler={handler} took duration={duration}')


def time_function(method):
    """
    A method decorator that logs the time taken to execute a given method
    """

    if inspect.iscoroutinefunction(method):
        @wraps(method)
        async def invoke_method_with_timer(*args, **kwargs):
            stopwatch = _begin_stopwatch()
            try:
                return await method(*args, **kwargs)
            finally:
                _log_time(stopwatch.stop_timer(), method.__name__)
    else:
        @wraps(method)
        def invoke_method_with_timer(*args, **kwargs):
            stopwatch = _begin_stopwatch()
            try:
                return method(*args, **kwargs)
            finally:
                _log_time(stopwatch.stop_timer(), method.__name__)

    return invoke_method_with_timer


def time_request(method):
    """
    A method to be used with tornado end points to extract their calling details and time their execution, this
    mainly holds as a placeholder if any extra data is required from the call
    """
    if inspect.iscoroutinefunction(method):
        async def method_wrapper(*args, **kwargs):
            handler = args[0]
            stopwatch = _begin_stopwatch()

            try:
                return await method(*args, **kwargs)
            finally:
                _log_tornado_time(stopwatch.stop_timer(),
                                  handler.__class__.__name__,
                                  handler.request.method.lower())

        return method_wrapper
    else:
        def method_wrapper(*args, **kwargs):
            handler = args[0]
            stopwatch = _begin_stopwatch()

            try:
                return method(*args, **kwargs)
            finally:
                _log_tornado_time(stopwatch.stop_timer(),
                                  handler.__class__.__name__,
                                  handler.request.method.lower())

    return method_wrapper

