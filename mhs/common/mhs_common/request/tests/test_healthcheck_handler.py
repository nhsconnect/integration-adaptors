import tornado.testing
from tornado.web import Application

from mhs_common.request import healthcheck_handler


class TestHealthcheckHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return tornado.web.Application([(r'/healthcheck', healthcheck_handler.HealthcheckHandler)])

    def test_get(self):
        response = self.fetch('/healthcheck', method='GET')

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode(), '')
