from unittest import TestCase
from unittest.mock import patch

from common.utilities import timing
from common.utilities.test_utilities import async_test


class TestTimeUtilities(TestCase):

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    def test_invoke_with_time(self, log_mock, time_mock):
        time_mock.return_value = 5
        self.sleep_method()
        log_mock.assert_called_with("Method 'sleep_method' called, executed in: 5s")

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    def test_exception_thrown_whilst_timing(self, log_mock, time_mock):
        time_mock.return_value = 5
        try:
            self.throw_error_method()
        except ValueError:
            pass

        log_mock.assert_called_with("Method 'throw_error_method' called, executed in: 5s")

    @patch('time.time')
    def test_stopwatch(self, time_mock):
        stopwatch = timing.StopWatch()
        time_mock.return_value = 0
        stopwatch.start_timer()
        time_mock.return_value = 5
        result = stopwatch.stop_timer()

        self.assertEqual(result, 5)

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    def test_invoke_with_time_rounding(self, log_mock, time_mock):
        time_mock.return_value = 5.1236
        self.sleep_method()
        log_mock.assert_called_with("Method 'sleep_method' called, executed in: 5.124s")

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    def test_invoke_with_time_parameters(self, log_mock, time_mock):
        time_mock.return_value = 5
        self.take_parameters("whew", 1, [2], {3: 3})
        log_mock.assert_called_with("Method 'take_parameters' called, executed in: 5s")

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    @async_test
    async def test_invoke_with_time_async_method(self, log_mock, time_mock):
        time_mock.return_value = 5
        await self.async_method()
        log_mock.assert_called_with("Method 'async_method' called, executed in: 5s")

    @timing.time_method
    def sleep_method(self):
        pass

    @timing.time_method
    def throw_error_method(self):
        raise ValueError("Whew")

    @timing.time_method
    def take_parameters(self, check, one, two, three):
        assert check is not None
        assert one is not None
        assert two is not None
        assert three is not None

    @timing.time_method
    async def async_method(self):
        pass
