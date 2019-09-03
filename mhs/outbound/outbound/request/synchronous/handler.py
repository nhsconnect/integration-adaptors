"""This module defines the outbound synchronous request handler component."""

from typing import Dict, Any
import tornado.locks
import tornado.web
import mhs_common.workflow as workflow
from mhs_common.configuration import configuration_manager
from utilities import integration_adaptors_logger as log, message_utilities, timing
import mhs_common.state.work_description as wd


logger = log.IntegrationAdaptorsLogger('MHS_OUTBOUND_HANDLER')


class SynchronousHandler(tornado.web.RequestHandler):
    """A Tornado request handler intended to handle incoming HTTP requests from a supplier system."""

    def initialize(self, workflows: Dict[str, workflow.CommonWorkflow],
                   config_manager: configuration_manager.ConfigurationManager):
        """Initialise this request handler with the provided configuration values.

        :param workflows: The workflows to use to send messages.
        :param config_manager: The object that can be used to obtain configuration details.
        """
        self.workflows = workflows
        self.config_manager = config_manager

    @timing.time_request
    async def post(self):
        message_id = self._extract_message_id()
        correlation_id = self._extract_correlation_id()

        logger.info('0006', 'Outbound POST received. {Request}', {'Request': str(self.request)})

        body = self.request.body.decode()
        if not body:
            logger.warning('0009', 'Body missing from request')
            raise tornado.web.HTTPError(400, 'Body missing from request', reason='Body missing from request')

        interaction_id = self._extract_interaction_id()

        interaction_details = self._get_interaction_details(interaction_id)
        if interaction_details is None:
            logger.warning('0007', 'Unknown {InteractionId} in request', {'InteractionId': interaction_id})
            raise tornado.web.HTTPError(404, f'Unknown interaction ID: {interaction_id}',
                                        reason=f'Unknown interaction ID: {interaction_id}')

        try:
            wf = self.workflows[interaction_details['workflow']]
        except KeyError as e:
            logger.error('0008', "Weren't able to determine workflow for {InteractionId} . This likely is due to a "
                                 "misconfiguration in interactions.json", {"InteractionId": interaction_id})
            raise tornado.web.HTTPError(500,
                                        f"Couldn't determine workflow to invoke for interaction ID: {interaction_id}",
                                        reason=f"Couldn't determine workflow to invoke for interaction ID: "
                                        f"{interaction_id}") from e

        if self._is_sync_async(interaction_details):
            async_workflow: workflow.SyncAsyncWorkflow = self.workflows[workflow.SYNC_ASYNC]
            status, response, wdo = await async_workflow.handle_sync_async_outbound_message(message_id, correlation_id,
                                                                                            interaction_details, body,
                                                                                            wf)
            await self.return_sync_async_response(status, response, wdo)
        else:
            status, response = await wf.handle_outbound_message(message_id, correlation_id, interaction_details, body,
                                                                None)
            self._write_response(status, response)

    def _is_sync_async(self, inteaction_details):
        try:
            flag = inteaction_details['sync-async']
            return flag
        except KeyError:
            return False

    async def return_sync_async_response(self, status: int, response: str, wdo: wd.WorkDescription):
        try:
            self._write_response(status, response)
            await wdo.set_status(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED)
        except Exception as e:
            logger.error('0015', 'Failed to respond to supplier system {exception}', {'exception': e})
            await wdo.set_status(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND)


    def write_error(self, status_code: int, **kwargs: Any):
        self.set_header('Content-Type', 'text/plain')
        self.finish(f'{status_code}: {self._reason}')

    def _extract_message_id(self):
        message_id = self.request.headers.get('Message-Id', None)
        if not message_id:
            message_id = message_utilities.MessageUtilities.get_uuid()
            log.message_id.set(message_id)
            logger.info('0001', "Didn't receive message id in incoming request from supplier, so have generated a new "
                                "one.")
        else:
            log.message_id.set(message_id)
            logger.info('0002', 'Found message id on incoming request.')
        return message_id

    def _extract_correlation_id(self):
        correlation_id = self.request.headers.get('Correlation-Id', None)
        if not correlation_id:
            correlation_id = message_utilities.MessageUtilities.get_uuid()
            log.correlation_id.set(correlation_id)
            logger.info('0003', "Didn't receive correlation id in incoming request from supplier, so have generated a "
                                "new one.")
        else:
            log.correlation_id.set(correlation_id)
            logger.info('0004', 'Found correlation id on incoming request.')
        return correlation_id

    def _extract_interaction_id(self):
        try:
            interaction_id = self.request.headers['Interaction-Id']
        except KeyError as e:
            logger.warning('0005', 'Required Interaction-Id header not passed in request')
            raise tornado.web.HTTPError(404, 'Required Interaction-Id header not found',
                                        reason='Required Interaction-Id header not found') from e
        return interaction_id

    def _write_response(self, status: int, message: str) -> None:
        """Write the given message to the response.

        :param message: The message to write to the response.
        """
        logger.info('0010', 'Returning response with {HttpStatus}', {'HttpStatus': status})
        self.set_status(status)
        if 400 <= status:
            content_type = "text/plain"
        else:
            content_type = "text/xml"
        self.set_header("Content-Type", content_type)
        self.write(message)

    def _get_interaction_details(self, interaction_name: str) -> dict:
        return self.config_manager.get_interaction_details(interaction_name)
