import datetime
from unittest import TestCase
from unittest.mock import patch, Mock

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler
from utilities import timing
from utilities.test_utilities import async_test

DEFAULT_RETURN = "default"


class TestTimeUtilities(TestCase):

    @patch('time.perf_counter')
    def test_stopwatch(self, time_mock):
        stopwatch = timing.Stopwatch()
        time_mock.return_value = 0.0
        stopwatch.start_timer()
        time_mock.return_value = 5.0
        result = stopwatch.stop_timer()

        self.assertEqual(result, 5)

    @patch.object(timing, 'logger')
    def test_invoke_with_time_rounding(self, log_mock):
        with self.subTest("Default"):
            timing._log_time(5.1236, "yes")
            log_mock.info.assert_called_with('{FuncName} took {Duration} seconds',
                                             fparams={'FuncName': 'yes', 'Duration': 5.124})
        with self.subTest("Tornado"):
            timing._log_tornado_time(5.1236, "yes", "methodName")
            log_mock.info.assert_called_with('{FuncName} from {Handler} took {Duration} seconds',
                                             fparams={'FuncName': 'methodName', 'Handler': 'yes', 'Duration': 5.124})

    @patch('utilities.timing._log_time')
    @patch('utilities.timing.Stopwatch.stop_timer')
    @async_test
    async def test_invoke_with_time(self, time_mock, log_mock):
        time_mock.return_value = 5
        with self.subTest("Sync version"):
            res = self.default_method()
            log_mock.assert_called_with(5, 'default_method')
            self.assertEqual(DEFAULT_RETURN, res)

        with self.subTest("Async version"):
            res = await self.default_method_async()
            log_mock.assert_called_with(5, 'default_method_async')
            self.assertEqual(DEFAULT_RETURN, res)

    @patch('utilities.timing.Stopwatch.stop_timer')
    @patch('utilities.timing._log_time')
    @async_test
    async def test_exception_thrown_whilst_timing(self, log_mock, time_mock):
        time_mock.return_value = 10
        with self.subTest("Sync"):
            with self.assertRaises(ValueError):
                self.throw_error_method()
            log_mock.assert_called_with(10, 'throw_error_method')

        with self.subTest("Async"):
            with self.assertRaises(ValueError):
                await self.throw_error_method_async()

            log_mock.assert_called_with(10, 'throw_error_method_async')

    @patch('utilities.timing.Stopwatch.stop_timer')
    @patch.object(timing, 'logger')
    @async_test
    async def test_invoke_with_time_parameters(self, log_mock, time_mock):
        with self.subTest("Sync"):
            time_mock.return_value = 5
            res = self.take_parameters("whew", 1, [2], {3: 3})
            log_mock.info.assert_called_with('{FuncName} took {Duration} seconds',
                                             fparams={'FuncName': 'take_parameters', 'Duration': 5})
            self.assertEqual("whew1", res)
        with self.subTest("Async"):
            time_mock.return_value = 5
            res = await self.take_parameters_async("whew", 1, [2], {3: 3})
            log_mock.info.assert_called_with('{FuncName} took {Duration} seconds',
                                             fparams={'FuncName': 'take_parameters_async', 'Duration': 5})
            self.assertEqual("whew1", res)

    @patch('utilities.timing.Stopwatch.stop_timer')
    @patch.object(timing, 'logger')
    @async_test
    async def test_async_times_execution_correctly(self, log_mock, time_mock):
        time_mock.return_value = 0
        task = self.default_method_async()

        # check the method doesn't get timed until awaited
        time_mock.return_value = 2

        await task

        log_mock.info.assert_called_with('{FuncName} took {Duration} seconds',
                                         fparams={'FuncName': 'default_method_async', 'Duration': 2})

    @patch('utilities.timing.Stopwatch.stop_timer')
    @patch.object(timing, 'logger')
    @async_test
    async def test_invoke_with_time_varargs(self, log_mock, time_mock):
        with self.subTest("Sync"):
            time_mock.return_value = 5
            res = self.var_parameters("whew", 1, 2, 3, 4, 5)
            log_mock.info.assert_called_with('{FuncName} took {Duration} seconds',
                                             fparams={'FuncName': 'var_parameters', 'Duration': 5})
            self.assertEqual("whew12345", res)
        with self.subTest("Async"):
            time_mock.return_value = 5
            res = await self.var_parameters_async("whew", 1, "three", 4)
            log_mock.info.assert_called_with('{FuncName} took {Duration} seconds',
                                             fparams={'FuncName': 'var_parameters_async', 'Duration': 5})
            self.assertEqual("whew1three4", res)

    @patch('utilities.timing.datetime')
    def test_get_time(self, mock_datetime):
        mock_datetime.datetime.utcnow.return_value = datetime.datetime(2019, 1, 5, 12, 13, 14, 567)
        self.assertEqual('2019-01-05T12:13:14.000567Z', timing.get_time())

    @timing.time_function
    def default_method(self):
        return DEFAULT_RETURN

    @timing.time_function
    async def default_method_async(self):
        return DEFAULT_RETURN

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
        return self.take_parameters(check, one, two, three)

    @timing.time_function
    def var_parameters(self, *arg):
        return ''.join([str(string) for string in arg])

    @timing.time_function
    async def var_parameters_async(self, *arg):
        return self.var_parameters(*arg)


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


@patch.object(timing, 'logger')
class TestHTTPWrapperTimeUtilities(AsyncHTTPTestCase):

    duration = 5

    def get_app(self):
        self.sender = Mock()
        return Application([
            (r"/.*", FakeRequestHandler, {})
        ])

    def _assert_handler_data(self, response, expected_code, expected_body, expected_func_name, log_mock):
        self.assertEqual(response.code, expected_code)
        if expected_body:
            self.assertEqual(response.body.decode(), expected_body)
        log_mock.info.assert_called_with('{FuncName} from {Handler} took {Duration} seconds',
                                         fparams={
                                             'FuncName': expected_func_name,
                                             'Handler': 'FakeRequestHandler',
                                             'Duration': self.duration
                                         })

    @patch('utilities.timing.Stopwatch.stop_timer')
    def test_post_synchronous_message(self, time_mock, log_mock):
        time_mock.return_value = self.duration

        response = self.fetch(f"/", method="POST", body="{'test': 'tested'}")
        self._assert_handler_data(response, 200, 'hello', 'post', log_mock)

    @patch('utilities.timing.Stopwatch.stop_timer')
    def test_get_asynchronous_message(self, time_mock, log_mock):
        time_mock.return_value = self.duration

        response = self.fetch(f"/", method="GET")
        self._assert_handler_data(response, 200, 'hello', 'get', log_mock)

    @patch('utilities.timing.Stopwatch.stop_timer')
    def test_raise_exception(self, time_mock, log_mock):
        time_mock.return_value = self.duration

        response = self.fetch(f"/", method="PUT", body="{'test': 'tested'}")

        self._assert_handler_data(response, 500, None, 'put', log_mock)
