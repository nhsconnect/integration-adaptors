import logging
from datetime import timedelta
from typing import Callable, Dict

from tornado.locks import Event
from tornado.web import RequestHandler, HTTPError

from mhs.sender.sender import UnknownInteractionError, Sender


class ClientRequestHandler(RequestHandler):
    """A RequestHandler for client requests to this MHS."""

    def initialize(self, sender: Sender, callbacks: Dict[str, Callable[[str], None]], async_timeout: int):
        """Initialise this request handler with the provided configuration values.

        :param sender: The sender to use to send messages.
        :param callbacks: The dictionary of callbacks to use when awaiting an asynchronous response.
        :param async_timeout: The amount of time (in seconds) to wait for an asynchronous response.
        """
        self.sender = sender
        self.callbacks = callbacks
        self.async_response_received = Event()
        self.async_timeout = async_timeout

    async def post(self):
        logging.debug("Client POST received: %s", self.request)

        interaction_name = self.request.uri[1:]

        try:
            async_message_id, immediate_response = self.sender.send_message(interaction_name,
                                                                            self.request.body.decode())
            logging.debug("Message sent with ID '%s'. Received response: %s", async_message_id, immediate_response)

            if async_message_id is not None:
                # Async response expected.
                await self._pause_request(async_message_id)
            else:
                # No async response expected. Just return the response to our initial request.
                self._write_response(immediate_response)
        except UnknownInteractionError:
            raise HTTPError(404, "Unknown interaction ID: %s", interaction_name)

    async def _pause_request(self, async_message_id):
        """Pause the incoming request until an asynchronous response is received (or a timeout is hit).

        :param async_message_id: The ID of the request that expects an asynchronous response.
        :raises: An HTTPError if we timed out waiting for an asynchronous response.
        """
        self.callbacks[async_message_id] = self._write_async_response

        try:
            await self.async_response_received.wait(timedelta(seconds=self.async_timeout))
        except TimeoutError:
            raise HTTPError(log_message=f"Timed out waiting for a response to message {async_message_id}")

        del self.callbacks[async_message_id]

    def _write_response(self, message: str) -> None:
        """Write the given message to the response.

        :param message: The message to write to the response.
        """
        self.set_header("Content-Type", "text/xml")
        self.write(message)

    def _write_async_response(self, message: str) -> None:
        """Write the given message to the response and notify anyone waiting that this has been done.

        :param message: The message to write to the response.
        """
        self._write_response(message)
        self.async_response_received.set()
