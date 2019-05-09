import logging

from tornado.web import RequestHandler, HTTPError

from mhs.sender.sender import UnknownInteractionError


class ClientRequestHandler(RequestHandler):
    """A RequestHandler for client requests to this MHS."""

    def initialize(self, sender):
        """Initialise this request handler with the provided configuration values.

        :param sender: The sender to use to send messages.
        """
        self.sender = sender

    def post(self):
        logging.debug("Client POST received: %s", self.request)

        interaction_name = self.request.uri[1:]

        try:
            response = self.sender.send_message(interaction_name, self.request.body.decode())

            logging.debug("Message sent. Received response: %s", response)

            self.set_header("Content-Type", "text/xml")
            self.write(response)
        except UnknownInteractionError:
            raise HTTPError(404, "Unknown interaction ID: %s", interaction_name)
