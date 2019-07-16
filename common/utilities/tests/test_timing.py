
from unittest import TestCase
from unittest.mock import patch, Mock

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from common.utilities import timing
from common.utilities.test_utilities import async_test


class TestTimeUtilities(TestCase):

    @patch('time.perf_counter')
    def test_stopwatch(self, time_mock):
        stopwatch = timing.Stopwatch()
        time_mock.return_value = 0.0
        stopwatch.start_timer()
        time_mock.return_value = 5.0
        result = stopwatch.stop_timer()

        self.assertEqual(result, 5)

    @patch('logging.info')
    def test_invoke_with_time_rounding(self, log_mock):
        timing._log_time(5.1236, "yes")
        log_mock.assert_called_with('Method name=yes took duration=5.124')

    @patch('common.utilities.timing._log_time')
    @patch('common.utilities.timing.Stopwatch.stop_timer')
    @async_test
    async def test_invoke_with_time(self, time_mock, log_mock):
        time_mock.return_value = 5
        with self.subTest("Sync version"):
            res = self.default_method()
            log_mock.assert_called_with(5, 'default_method')
            self.assertEqual("slept", res)

        with self.subTest("Async version"):
            res = await self.default_method_async()
            log_mock.assert_called_with(5, 'default_method_async')
            self.assertEqual(5, res)

    @patch('common.utilities.timing.Stopwatch.stop_timer')
    @patch('common.utilities.timing._log_time')
    @async_test
    async def test_exception_thrown_whilst_timing(self, log_mock, time_mock):
        time_mock.return_value = 5
        with self.subTest("Sync"):
            try:
                self.throw_error_method()
            except ValueError:
                pass
            log_mock.assert_called_with(5, 'throw_error_method')

        with self.subTest("Async"):
            try:
                await self.throw_error_method_async()
            except ValueError:
                pass

            log_mock.assert_called_with(5, 'throw_error_method_async')

    @patch('common.utilities.timing.Stopwatch.stop_timer')
    @patch('logging.info')
    @async_test
    async def test_invoke_with_time_parameters(self, log_mock, time_mock):
        with self.subTest("Sync"):
            time_mock.return_value = 5
            res = self.take_parameters("whew", 1, [2], {3: 3})
            log_mock.assert_called_with('Method name=take_parameters took duration=5')
            self.assertEqual("whew1", res)
        with self.subTest("Async"):
            time_mock.return_value = 5
            res = await self.take_parameters_async("whew", 1, [2], {3: 3})
            log_mock.assert_called_with('Method name=take_parameters_async took duration=5')
            self.assertEqual("whew1", res)

    @patch('common.utilities.timing.Stopwatch.stop_timer')
    @patch('logging.info')
    @async_test
    async def test_async_times_execution_correctly(self, log_mock, time_mock):
        time_mock.return_value = 0
        task = self.default_method_async()

        # check the method doesn't get timed until awaited
        time_mock.return_value = 2

        await task

        log_mock.assert_called_with('Method name=default_method_async took duration=2')

    @patch('common.utilities.timing.Stopwatch.stop_timer')
    @patch('logging.info')
    @async_test
    async def test_invoke_with_time_varargs(self, log_mock, time_mock):
        with self.subTest("Sync"):
            time_mock.return_value = 5
            res = self.var_parameters("whew", 1, 2, 3, 4, 5)
            log_mock.assert_called_with('Method name=var_parameters took duration=5')
            self.assertEqual("whew12345", res)
        with self.subTest("Async"):
            time_mock.return_value = 5
            res = await self.var_parameters_async("whew", 1, "three", 4)
            log_mock.assert_called_with('Method name=var_parameters_async took duration=5')
            self.assertEqual("whew1three4", res)

    @timing.time_function
    def default_method(self):
        return "slept"

    @timing.time_function
    async def default_method_async(self):
        return 5

    @timing.time_function
    def throw_error_method(self):
        raise ValueError("Whew")

    @timing.time_function
    async def throw_error_method_async(self):
        raise ValueError("Whew")

    @timing.time_function
    def take_parameters(self, check, one, two, three):
        assert check is not None
        assert one is not None
        assert two is not None
        assert three is not None
        return check + str(one)

    @timing.time_function
    async def take_parameters_async(self, check, one, two, three):
        assert check is not None
        assert one is not None
        assert two is not None
        assert three is not None
        return check + str(one)

    @timing.time_function
    def var_parameters(self, *arg):
        return ''.join([str(string) for string in arg])

    @timing.time_function
    async def var_parameters_async(self, *arg):
        return ''.join([str(string) for string in arg])


class FakeRequestHandler(RequestHandler):

    @timing.time_request
    def post(self):
        self.write("hello")

    @timing.time_request
    async def get(self):
        self.write("hello")

    @timing.time_request
    def put(self):
        try:
            raise ValueError("Whew")
        finally:
            self.write("put")


class TestHTTPWrapperTimeUtilities(AsyncHTTPTestCase):

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r"/.*", FakeRequestHandler, {})
        ])

    def _assert_handler_data(self, response, expected_code, expected_body, expected_log, log_mock):
        self.assertEqual(response.code, expected_code)
        if expected_body:
            self.assertEqual(response.body.decode('utf8'), expected_body)
        log_mock.assert_called_with(expected_log)

    @patch('common.utilities.timing.Stopwatch.stop_timer')
    @patch('logging.info')
    def test_post_synchronous_message(self, log_mock, time_mock):
        time_mock.return_value = 5

        response = self.fetch(f"/", method="POST", body="{'test': 'tested'}")
        self._assert_handler_data(response, 200,
                                  "hello", 'method=post from handler=FakeRequestHandler took duration=5', log_mock)

    @patch('common.utilities.timing.Stopwatch.stop_timer')
    @patch('logging.info')
    def test_get_asynchronous_message(self, log_mock, time_mock):
        time_mock.return_value = 5

        response = self.fetch(f"/", method="GET")
        self._assert_handler_data(response, 200,
                                  "hello", 'method=get from handler=FakeRequestHandler took duration=5', log_mock)

    @patch('common.utilities.timing.Stopwatch.stop_timer')
    @patch('logging.info')
    def test_raise_exception(self,  log_mock, time_mock):
        time_mock.return_value = 5

        response = self.fetch(f"/", method="PUT", body="{'test': 'tested'}")

        self._assert_handler_data(response, 500,
                                  None, 'method=put from handler=FakeRequestHandler took duration=5', log_mock)
