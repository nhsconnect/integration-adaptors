import unittest
from unittest import mock

from utilities import test_utilities

from retry import retriable_action

DEFAULT_RETRIES = 3
DEFAULT_DELAY = 0.1


class TestRetriableAction(unittest.TestCase):
    def setUp(self):
        self.mock_action = mock.Mock()

    @test_utilities.async_test
    async def test_should_only_try_once_if_action_succeeds(self):
        expected_result = "Result"
        self.mock_action.return_value = test_utilities.awaitable(expected_result)

        result = await retriable_action.RetriableAction(self.mock_action, retries=DEFAULT_RETRIES, delay=DEFAULT_DELAY) \
            .execute()

        self.assertTrue(result.is_successful, "The action should be reported as successful.")
        self.assertEqual(expected_result, result.result, "The expected result should be returned.")
        self.assertIsNone(result.exception, "No exception should be reported.")
        self.assertEqual(1, self.mock_action.call_count, "The action should only be executed once.")

    @test_utilities.async_test
    async def test_should_retry_if_action_fails(self):
        expected_result = "Result"
        self.mock_action.side_effect = [Exception, test_utilities.awaitable(expected_result)]

        result = await retriable_action.RetriableAction(self.mock_action, retries=DEFAULT_RETRIES,
                                                        delay=DEFAULT_DELAY) \
            .execute()

        self.assertTrue(result.is_successful, "The action should be reported as successful.")
        self.assertEqual(expected_result, result.result, "The expected result should be returned.")
        self.assertIsNone(result.exception, "No exception should be reported.")
        self.assertEqual(2, self.mock_action.call_count, "The action should be executed twice.")

    @test_utilities.async_test
    async def test_should_retry_up_to_maximum_if_action_keeps_failing(self):
        exception_raised = Exception()
        self.mock_action.side_effect = exception_raised

        result = await retriable_action.RetriableAction(self.mock_action, retries=DEFAULT_RETRIES,
                                                        delay=DEFAULT_DELAY) \
            .execute()

        self.assertFalse(result.is_successful, "The action should be reported as unsuccessful.")
        self.assertIsNone(result.result, "No result should be returned.")
        self.assertEqual(exception_raised, result.exception, "The exception raised should be reported.")
        self.assertEqual(1 + DEFAULT_RETRIES, self.mock_action.call_count,
                         f"The action should be executed once and then retried {DEFAULT_RETRIES} times.")

    @test_utilities.async_test
    async def test_should_try_once_if_retries_set_to_zero(self):
        self.mock_action.side_effect = Exception

        await retriable_action.RetriableAction(self.mock_action, retries=0, delay=DEFAULT_DELAY).execute()

        self.assertEqual(1, self.mock_action.call_count,
                         "The action should be tried once if zero retries are requested.")

    @test_utilities.async_test
    async def test_should_try_twice_if_retries_set_to_one(self):
        self.mock_action.side_effect = Exception

        await retriable_action.RetriableAction(self.mock_action, retries=1, delay=DEFAULT_DELAY).execute()

        self.assertEqual(2, self.mock_action.call_count,
                         "The action should be tried twice if one retry is requested.")

    @test_utilities.async_test
    async def test_should_report_success_if_custom_success_check_passes(self):
        action = retriable_action.RetriableAction(self.mock_action, retries=DEFAULT_RETRIES, delay=DEFAULT_DELAY) \
            .with_success_check(lambda r: r == "success")

        self.mock_action.return_value = test_utilities.awaitable("success")

        result = await action.execute()

        self.assertTrue(result.is_successful, "The action should be reported as successful.")
        self.assertEqual(1, self.mock_action.call_count, "The action should only be executed once.")

    @test_utilities.async_test
    async def test_should_report_failure_if_custom_success_check_fails(self):
        action = retriable_action.RetriableAction(self.mock_action, retries=DEFAULT_RETRIES, delay=DEFAULT_DELAY) \
            .with_success_check(lambda r: r == "success")

        self.mock_action.return_value = test_utilities.awaitable("failure")

        result = await action.execute()

        self.assertFalse(result.is_successful, "The action should be reported as unsuccessful.")
        self.assertEqual(1 + DEFAULT_RETRIES, self.mock_action.call_count,
                         f"The action should be executed once and then retried {DEFAULT_RETRIES} times.")

    @test_utilities.async_test
    async def test_should_not_retry_if_non_retriable_exception_raised(self):
        exception_raised = ValueError()
        self.mock_action.side_effect = exception_raised

        result = await retriable_action.RetriableAction(self.mock_action, retries=DEFAULT_RETRIES,
                                                        delay=DEFAULT_DELAY) \
            .with_retriable_exception_check(lambda e: isinstance(e, TypeError)) \
            .execute()

        self.assertFalse(result.is_successful, "The action should be reported as unsuccessful.")
        self.assertIsNone(result.result, "No result should be returned.")
        self.assertEqual(exception_raised, result.exception, "The exception raised should be reported.")
        self.assertEqual(1, self.mock_action.call_count,
                         "The action should not be retried if a non-retriable exception is raised")

    @mock.patch("asyncio.sleep")
    @test_utilities.async_test
    async def test_should_only_sleep_between_retries(self, mock_sleep):
        self.mock_action.side_effect = Exception
        mock_sleep.return_value = test_utilities.awaitable(None)

        await retriable_action.RetriableAction(self.mock_action, retries=DEFAULT_RETRIES, delay=DEFAULT_DELAY) \
            .execute()

        self.assertEqual(DEFAULT_RETRIES, mock_sleep.call_count,
                         f"When action is executed {DEFAULT_RETRIES + 1} times, sleep should only be called "
                         f"{DEFAULT_RETRIES} times")

    @mock.patch("asyncio.sleep")
    @test_utilities.async_test
    async def test_should_not_sleep_if_no_retries(self, mock_sleep):
        self.mock_action.side_effect = Exception
        mock_sleep.return_value = test_utilities.awaitable(None)

        await retriable_action.RetriableAction(self.mock_action, retries=0, delay=DEFAULT_DELAY) \
            .execute()

        self.assertEqual(0, mock_sleep.call_count, f"When action is not retried, sleep should never be called.")
