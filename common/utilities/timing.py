import logging
import time
from functools import wraps


class StopWatch:

    start_time = None

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        end_time = time.time()
        diff = end_time - self.start_time
        return diff


def time_method(method):
    """
    A method decorator that logs the time taken to

    :param method:
    :return:
    """

    @wraps(method)
    def invoke_method_with_timer(*args, **kwargs):
        stopwatch = StopWatch()
        stopwatch.start_timer()
        try:
            return method(*args, **kwargs)
        finally:
            duration = stopwatch.stop_timer()
            duration = round(duration, 3)
            logging.info(f"Method '{method.__name__}' called, executed in: {duration}s")

    return invoke_method_with_timer


def log_request(method):
    """
    A method to be used with tornado end points to extract their calling details and time their execution, this
    mainly holds as a placeholder if any extra data is required from the call
    """
    def method_wrapper(*args, **kwargs):

        # Gets the 'self' of the caller
        handler = args[0]

        log_details = {
            'handler': handler.__class__.__name__,
            'method': handler.request.method.lower(),
            'requestBody': handler.request.body
        }

        stopwatch = StopWatch()
        stopwatch.start_timer()

        try:
            return method(*args, **kwargs)
        finally:
            duration = stopwatch.stop_timer()
            duration = round(duration, 3)
            log_details['duration'] = duration
            logging.info(f"{log_details}")

    return method_wrapper
