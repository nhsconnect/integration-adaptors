import json
import logging
import math
import time
from unittest import TestCase
from unittest.mock import patch, Mock

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

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

    @patch('logging.info')
    @async_test
    def test_invoke_with_time_async_method(self, log_mock):
        self.actual_sleep()
        log_mock.assert_called_with("Method 'async_method' called, executed in: 5s")

    @timing.time_method
    async def actual_sleep(self):
        time.sleep(1)


class FakeRequestHandler(RequestHandler):

    @timing.log_request
    def post(self):
        pass

    @timing.async_log_request
    async def get(self):
        time.sleep(0.5)


class TestHTTPWrapperTimeUtilities(AsyncHTTPTestCase):

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r"/.*", FakeRequestHandler, {})
        ])

    @patch('time.sleep')
    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    def test_post_synchronous_message(self, log_mock, time_mock, sleep_mock):
        time_mock.return_value = 5
        expected_response = "Hello world!"
        self.sender.prepare_message.return_value = False, None, None
        self.sender.send_message.return_value = expected_response

        response = self.fetch(f"/", method="POST", body="{'test': 'tested'}")

        self.assertEqual(response.code, 200)
        log = '{\'handler\': \'FakeRequestHandler\', \'method\': \'post\', ' \
              '\'requestBody\': b"{\'test\': \'tested\'}", \'duration\': 5}'
        log_mock.assert_called_with(log)

    @patch('logging.info')
    def test_get_asynchronous_message_whew(self, log_mock):
        expected_response = "Hello world!"
        self.sender.prepare_message.return_value = False, None, None
        self.sender.send_message.return_value = expected_response

        response = self.fetch(f"/", method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(len(log_mock.call_args_list), 1)

        call = log_mock.call_args_list[0]
        args, kwargs = call
        input_dict = json.loads(args[0].replace("\'", "\""))

        print(input_dict["duration"] == 0.5)
        self.assertTrue(math.isclose(input_dict["duration"], 0.5, rel_tol=0.15))