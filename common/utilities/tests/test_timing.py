import asyncio
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

    @patch('common.utilities.timing._log_time')
    @patch('common.utilities.timing.StopWatch.stop_timer')
    def test_invoke_with_time(self, time_mock, log_mock):
        time_mock.return_value = 5
        res = self.sleep_method()
        log_mock.assert_called_with(5, 'sleep_method')
        self.assertEqual("slept", res)

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('common.utilities.timing._log_time')
    def test_invoke_with_time_async(self, log_mock, time_mock):
        time_mock.return_value = 5
        res = self.sleep_method()
        log_mock.assert_called_with(5, 'sleep_method')
        self.assertEqual("slept", res)

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('common.utilities.timing._log_time')
    def test_exception_thrown_whilst_timing(self, log_mock, time_mock):
        time_mock.return_value = 5
        try:
            self.throw_error_method()
        except ValueError:
            pass

        log_mock.assert_called_with(5, 'throw_error_method')

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('common.utilities.timing._log_time')
    @async_test
    async def test_exception_thrown_whilst_timing_async(self, log_mock, time_mock):
        time_mock.return_value = 5
        try:
            await self.throw_error_method_async()
        except ValueError:
            pass

        log_mock.assert_called_with(5, 'throw_error_method_async')

    @patch('time.perf_counter')
    def test_stopwatch(self, time_mock):
        stopwatch = timing.StopWatch()
        time_mock.return_value = 0.0
        stopwatch.start_timer()
        time_mock.return_value = 5.0
        result = stopwatch.stop_timer()

        self.assertEqual(result, 5)

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('common.utilities.timing._log_time')
    def test_invoke_with_time_rounding(self, log_mock, time_mock):
        time_mock.return_value = 5.1236
        res = self.sleep_method()

        log_mock.assert_called_with(5.1236, 'sleep_method')
        self.assertEqual("slept", res)

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    def test_invoke_with_time_parameters(self, log_mock, time_mock):
        time_mock.return_value = 5
        res = self.take_parameters("whew", 1, [2], {3: 3})
        log_mock.assert_called_with('Method name=take_parameters took duration=5')
        self.assertEqual("whew1", res)

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    @async_test
    async def test_invoke_with_time_parameters(self, log_mock, time_mock):
        time_mock.return_value = 5
        res = await self.take_parameters_async("whew", 1, [2], {3: 3})
        log_mock.assert_called_with('Method name=take_parameters_async took duration=5')
        self.assertEqual("whew1", res)

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    @async_test
    async def test_invoke_with_time_fake_async_method(self, log_mock, time_mock):
        time_mock.return_value = 5
        res = await self.async_method()
        log_mock.assert_called_with('Method name=async_method took duration=5')
        self.assertEqual(5, res)

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    @async_test
    async def test_async_times_execution_correctly(self, log_mock, time_mock):
        time_mock.return_value = 0
        task = self.async_method()

        # check the method doesn't get timed until awaited
        time_mock.return_value = 2

        await task

        log_mock.assert_called_with('Method name=async_method took duration=2')

    @timing.time_function
    def sleep_method(self):
        return "slept"

    @timing.time_function
    def throw_error_method(self):
        raise ValueError("Whew")

    @timing.time_function
    def take_parameters(self, check, one, two, three):
        assert check is not None
        assert one is not None
        assert two is not None
        assert three is not None
        return check + str(one)

    @timing.time_function
    async def async_method(self):
        return 5

    @timing.time_function
    async def throw_error_method_async(self):
        raise ValueError("Whew")

    @timing.time_function
    async def take_parameters_async(self, check, one, two, three):
        assert check is not None
        assert one is not None
        assert two is not None
        assert three is not None
        return check + str(one)


class FakeRequestHandler(RequestHandler):

    @timing.time_request
    def post(self):
        self.write("hello")

    @timing.time_request
    async def get(self):
        self.write("hello")


class TestHTTPWrapperTimeUtilities(AsyncHTTPTestCase):

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r"/.*", FakeRequestHandler, {})
        ])

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    def test_post_synchronous_message(self, log_mock, time_mock):
        time_mock.return_value = 5

        response = self.fetch(f"/", method="POST", body="{'test': 'tested'}")

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf8'), "hello")
        log_mock.assert_called_with('method=post from handler=FakeRequestHandler took duration=5')

    @patch('common.utilities.timing.StopWatch.stop_timer')
    @patch('logging.info')
    def test_get_asynchronous_message(self, log_mock, time_mock):
        time_mock.return_value = 5

        response = self.fetch(f"/", method="GET")

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf8'), "hello")
        log_mock.assert_called_with('method=get from handler=FakeRequestHandler took duration=5')
