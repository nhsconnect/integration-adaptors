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
            logging.info(f"Method '{method.__name__}' called, executed in: {duration}s")

    return invoke_method_with_timer
