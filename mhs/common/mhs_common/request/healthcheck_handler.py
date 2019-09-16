import tornado.web


class HealthcheckHandler(tornado.web.RequestHandler):
    """
    A Tornado request handler that returns an empty HTTP 200 response for any GET requests, without
    doing anything else. This handler is intended to be hit by anything that wants to check that the
    application is running ie for load balancers to do healthchecks.
    """

    async def get(self):
        self.set_status(200)
