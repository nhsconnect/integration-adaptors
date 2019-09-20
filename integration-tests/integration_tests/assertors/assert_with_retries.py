import time
from typing import Callable


class AssertWithRetries(object):

    def __init__(self, retry_count: int):
        self.retry_count = retry_count

    def assert_condition_met(self, func: Callable[[], bool]):
        for retry in range(0, self.retry_count):
            result = func()
            if result:
                return

            time.sleep(1)

        raise Exception(f"Unable to meet condition within retries: {self.retry_count}")