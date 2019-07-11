from unittest import TestCase
from unittest.mock import patch

from common.utilities import timing


class TestTimeUtilities(TestCase):

    @timing.time_method
    def sleep_method(self):
        pass

    @timing.time_method
    def throw_error_method(self):
        raise ValueError("Whew")

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
