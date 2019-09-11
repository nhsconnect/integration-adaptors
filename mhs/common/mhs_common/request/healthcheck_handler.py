import tornado.web


class HealthcheckHandler(tornado.web.RequestHandler):

    async def get(self):
        self.set_status(200)
