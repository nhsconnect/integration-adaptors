"""
Provides a way of asserting a condition is met within a number of retries in order to avoid test timing issues
"""
import time
from typing import Callable


class AssertWithRetries(object):
    """
    Asserts a condition is met within a number of retries, with a synchronous 1 second wait between each retry.
    """

    def __init__(self, retry_count: int):
        self.retry_count = retry_count

    def assert_condition_met(self, func: Callable[[], bool]) -> None:
        """
        Asserts a condition is met within the number of retries
        :param func: condition to be met
        :return: None, or throws exception if condition is not met
        """
        for retry in range(0, self.retry_count):
            result = func()
            if result:
                return

            time.sleep(1)

        raise Exception(f"Unable to meet condition within retries: {self.retry_count}")
