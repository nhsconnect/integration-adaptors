"""This module defines the outbound synchronous request handler component."""

import datetime
from typing import Dict, Callable

import tornado.locks
import tornado.web

import mhs.common.workflow.common as common_workflow
import mhs.common.workflow.sync_async as sync_async_workflow
import mhs.outbound.request.common as common
from mhs.common.configuration import configuration_manager
from utilities import integration_adaptors_logger as log, message_utilities

logger = log.IntegrationAdaptorsLogger('MHS_OUTBOUND_HANDLER')


class SynchronousHandler(common.CommonOutbound, tornado.web.RequestHandler):
    """A Tornado request handler intended to handle incoming HTTP requests from a supplier system."""

    def initialize(self, workflow: sync_async_workflow.SyncAsyncWorkflow,
                   config_manager: configuration_manager.ConfigurationManager,
                   callbacks: Dict[str, Callable[[str], None]], async_timeout: int):
        """Initialise this request handler with the provided configuration values.

        :param workflow: The workflow to use to send messages.
        :param config_manager: The object that can be used to obtain configuration details.
        :param callbacks: The dictionary of callbacks to use when awaiting an asynchronous response.
        :param async_timeout: The amount of time (in seconds) to wait for an asynchronous response.
        """
        self.workflow = workflow
        self.config_manager = config_manager
        self.callbacks = callbacks
        self.async_response_received = tornado.locks.Event()
        self.async_timeout = async_timeout

    async def post(self):
        message_id = self.request.headers.get('Message-Id', None)
        log.message_id.set(message_id)
        if not message_id:
            message_id = message_utilities.MessageUtilities.get_uuid()
            log.message_id.set(message_id)
            logger.info('0006', "Didn't receive message id in incoming request from supplier, so have generated a new "
                                "one.")
        else:
            logger.info('0007', 'Found message id on incoming request.')

        correlation_id = self.request.headers.get('Correlation-Id', None)
        log.correlation_id.set(correlation_id)
        if not correlation_id:
            correlation_id = message_utilities.MessageUtilities.get_uuid()
            log.correlation_id.set(correlation_id)
            logger.info('0008', "Didn't receive correlation id in incoming request from supplier, so have generated a "
                                "new one.")
        else:
            logger.info('0009', 'Found correlation id on incoming request.')

        try:
            interaction_name = self.request.headers['Interaction-Id']
        except KeyError as e:
            logger.warning('0005', 'Required Interaction-Id header not passed in request {MessageId}',
                           {'MessageId': message_id})
            raise tornado.web.HTTPError(404, 'Required Interaction-Id header not found') from e

        logger.info('0001', 'Client POST received. {Request}', {'Request': str(self.request)})

        try:
            interaction_details = self._get_interaction_details(interaction_name)
            interaction_is_async, message = self.workflow.prepare_message(interaction_details,
                                                                          self.request.body.decode(),
                                                                          message_id)

            if interaction_is_async:
                self.callbacks[message_id] = self._write_async_response
                logger.info('0002', 'Added callback for asynchronous message with {MessageId}',
                            {'MessageId': message_id})

            immediate_response = self.workflow.send_message(interaction_details, message)

            if interaction_is_async:
                await self._pause_request(message_id)
            else:
                # No async response expected. Just return the response to our initial request.
                self._write_response(immediate_response)

        except common_workflow.UnknownInteractionError as e:
            raise tornado.web.HTTPError(404, "Unknown interaction ID: %s", interaction_name) from e
        finally:
            if message_id in self.callbacks:
                del self.callbacks[message_id]

    async def _pause_request(self, async_message_id):
        """Pause the incoming request until an asynchronous response is received (or a timeout is hit).

        :param async_message_id: The ID of the request that expects an asynchronous response.
        :raises: An HTTPError if we timed out waiting for an asynchronous response.
        """
        try:
            logger.info('0003', 'Waiting for asynchronous response to message with {MessageId}',
                        {'MessageId': async_message_id})
            await self.async_response_received.wait(datetime.timedelta(seconds=self.async_timeout))
        except TimeoutError:
            raise tornado.web.HTTPError(log_message=f"Timed out waiting for a response to message {async_message_id}")

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
        logger.info('0004', 'Received asynchronous response containing message {Message}', {'Message': message})
        self._write_response(message)
        self.async_response_received.set()

    def _get_interaction_details(self, interaction_name: str) -> dict:
        interaction_details = self.config_manager.get_interaction_details(interaction_name)

        if not interaction_details:
            raise common_workflow.UnknownInteractionError(interaction_name)

        return interaction_details
