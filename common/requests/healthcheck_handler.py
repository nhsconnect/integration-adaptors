import tornado.web


class HealthcheckHandler(tornado.web.RequestHandler):
    """
    A Tornado request handler that returns an empty HTTP 200 response for any GET requests, without
    doing anything else. This handler is intended to be hit by anything that wants to check that the
    application is running ie for load balancers to do healthchecks.
    """

    async def get(self):
        """
        ---
        summary: Healthcheck endpoint
        description: >-
          This endpoint just returns a HTTP 200 response and does no further processing. This endpoint
          is intended to be used by load balancers/other infrastructure to check that the server is
          running.
        operationId: getHealthcheck
        responses:
          200:
            description: The only response this endpoint returns.
        """
        self.set_status(200)
