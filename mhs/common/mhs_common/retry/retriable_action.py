from __future__ import annotations

import asyncio
from typing import Callable, Awaitable

from utilities import integration_adaptors_logger

logger = integration_adaptors_logger.IntegrationAdaptorsLogger('RETRIABLE_ACTION')


class RetriableAction(object):
    """Responsible for retrying an action a configurable number of times with a configurable delay"""

    def __init__(self, action: Callable[[], Awaitable[object]], retries: int, delay: float):
        """

        :param action: The action to be retried.
        :param retries: The number of times to retry the action if it fails. The initial attempt will always occur.
        :param delay: The delay (in seconds) between retries.
        """
        self.action = action
        self.retries = retries
        self.delay = delay
        self.retriable_exception_check = lambda exception: True
        self.success_check = lambda result: True

        logger.info("0001", "Configuring a retriable action with {action}, {retries} and {delay}",
                    {"action": action, "retries": retries, "delay": delay})

    def with_success_check(self, success_check: Callable[[object], bool]) -> RetriableAction:
        """Set a callable that can be used to determine whether the result of the action was a success.

        This callable should accept the result of the action as a parameter and return True to identify that the result
        represents a successful call or False to represent a failure. If this method returns False, the action will be
        retried.

        :param success_check: The callable to use to check whether the action's result represents a successful call.
        :return self
        """
        logger.info("0002", "Setting retriable action's success check to {success_check}",
                    {"success_check": success_check})
        self.success_check = success_check
        return self

    def with_retriable_exception_check(self, exception_check: Callable[[Exception], bool]) -> RetriableAction:
        """Set a callable that can be used to determine whether an exception raised by the action will prompt a retry.

        :param exception_check: The callable to use to check whether the exception raised by the action should prompt a
        retry.
        :return self
        """
        logger.info("0003", "Setting retriable action's retriable exception check to {exception_check}",
                    {"exception_check": exception_check})
        self.retriable_exception_check = exception_check
        return self

    async def execute(self) -> RetriableActionResult:
        """Execute the action, retrying as necessary.

        :return: A RetriableActionResult that represents the result of the final attempt to perform the specified
        action.
        """
        result = await self._execute_action()

        if self._retry_required(result):
            for i in range(self.retries):
                logger.info("0004", "Sleeping for {delay} seconds before retrying {action}.",
                            {"delay": self.delay, "action": self.action})
                await asyncio.sleep(self.delay)

                result = await self._execute_action()

                if not self._retry_required(result):
                    break

                if i == self.retries - 1:
                    logger.error("0005", "Maximum number of retries performed. {action} has failed.",
                                 {"action": self.action})

        return result

    async def _execute_action(self) -> RetriableActionResult:
        result = RetriableActionResult()

        try:
            logger.info("0006", "About to try {action}.", {"action": self.action})
            action_result = await self.action()

            result.result = action_result
            result.is_successful = self.success_check(action_result)
            logger.info("0007", "{action} completed. {is_successful}",
                        {"action": self.action, "is_successful": result.is_successful})
        except Exception as e:
            logger.error("0008", "{action} raised an exception. {exception}",
                         {"action": self.action, "exception": e})
            result.exception = e

        return result

    def _retry_required(self, action_result: RetriableActionResult) -> bool:
        retry_required = True

        if action_result.is_successful:
            logger.info("0009", "{action} was successful. Retry not required.", {"action": self.action})
            retry_required = False

        if not self._exception_is_retriable(action_result.exception):
            logger.info("0010", "{action} raised a non-retriable exception. Retry not required.",
                        {"action": self.action})
            retry_required = False

        logger.info("0011", "{retry_required} for {action}", {"retry_required": retry_required, "action": self.action})
        return retry_required

    def _exception_is_retriable(self, exception: Exception) -> bool:
        return self.retriable_exception_check(exception)


class RetriableActionResult(object):
    """Represents the result of executing a RetriableAction.

    Attributes:
        - is_successful: A boolean indicating whether the action completed successfully or not.
        - result: The value returned by the action.
        - exception: Any exception raised by the action.
    """

    def __init__(self, is_successful: bool = False, result: object = None, exception: Exception = None):
        """Create a new RetriableActionResult with the provided parameters.

        :param is_successful: Whether the action completed successfully or not.
        :param result: The value returned by the action. May not be set if the action did not complete successfully.
        :param exception: Any exception raised by the action. May not be set if the action completed successfully.
        """
        self.is_successful = is_successful
        self.result = result
        self.exception = exception
