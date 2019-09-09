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
        interaction_id = self._extract_interaction_id()
        sync_async_header = self._extract_sync_async_header()

        logger.info('0006', 'Outbound POST received. {Request}', {'Request': str(self.request)})

        body = self._parse_body()

        interaction_details = self._retrieve_interaction_details(interaction_id)
        wf = self._extract_default_workflow(interaction_details, interaction_id)
        sync_async_interaction_config = self._extract_sync_async_from_interaction_details(interaction_details)

        if self._should_invoke_sync_async_workflow(sync_async_interaction_config, sync_async_header):
            await self._invoke_sync_async(message_id, correlation_id, interaction_details, body, wf)
        else:
            await self.invoke_default_workflow(message_id, correlation_id, interaction_details, body, wf)

    async def return_sync_async_response(self, status: int, response: str, wdo: wd.WorkDescription):
        try:
            self._write_response(status, response)
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_SUCCESSFULLY_RESPONDED)
        except Exception as e:
            logger.error('0015', 'Failed to respond to supplier system {exception}', {'exception': e})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_SYNC_ASYNC_MESSAGE_FAILED_TO_RESPOND)

    def _parse_body(self):
        body = self.request.body.decode()
        if not body:
            logger.warning('0009', 'Body missing from request')
            raise tornado.web.HTTPError(400, 'Body missing from request', reason='Body missing from request')
        return body

    def write_error(self, status_code: int, **kwargs: Any):
        self.set_header('Content-Type', 'text/plain')
        self.finish(f'{status_code}: {self._reason}')

    def _extract_sync_async_header(self):
        sync_async_header = self.request.headers.get('sync-async', None)
        if not sync_async_header:
            logger.warning('0031', 'Failed to parse sync-async header from message')
            raise tornado.web.HTTPError(400, 'Sync-Async header missing', reason='Sync-Async header missing')
        if sync_async_header == 'true':
            return True
        else:
            return False

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

    def _extract_default_workflow(self, interaction_details, interaction_id):
        try:
            wf = self.workflows[interaction_details['workflow']]
        except KeyError as e:
            logger.error('0008', "Wasn't able to determine workflow for {InteractionId} . This likely is due to a "
                                 "misconfiguration in interactions.json", {"InteractionId": interaction_id})
            raise tornado.web.HTTPError(500,
                                        f"Couldn't determine workflow to invoke for interaction ID: {interaction_id}",
                                        reason=f"Couldn't determine workflow to invoke for interaction ID: "
                                        f"{interaction_id}") from e
        return wf

    def _extract_sync_async_from_interaction_details(self, interaction_details):
        is_sync_async = interaction_details.get('sync-async')
        if is_sync_async is None:
            logger.error('0032', 'Failed to retrieve sync-async flag from interactions.json')
            raise tornado.web.HTTPError(500, f'Failed to parse sync-async flag from interactions.json file',
                                        reason='Failed to parse sync-async flag from interactions file for this '
                                               'interaction, contact your administrator')
        return is_sync_async

    def _should_invoke_sync_async_workflow(self, interaction_config, sync_async_header):
        print(interaction_config)
        print(sync_async_header)
        if interaction_config and sync_async_header:
            return True
        elif (not interaction_config) and sync_async_header:
            logger.error('0033', 'Message header requested sync-async wrap for un-supported sync-async')
            raise tornado.web.HTTPError(400, f'Message header requested sync-async wrap for un-supported sync-async',
                                        reason='Message header requested sync-async wrap for a message pattern'
                                               'that does not support sync-async')
        elif interaction_config and (not sync_async_header):
            return False
        elif (not interaction_config) and (not sync_async_header):
            return False

    async def _invoke_sync_async(self, message_id, correlation_id, interaction_details, body, async_workflow):
        sync_async_workflow: workflow.SyncAsyncWorkflow = self.workflows[workflow.SYNC_ASYNC]
        status, response, wdo = await sync_async_workflow.handle_sync_async_outbound_message(message_id,
                                                                                             correlation_id,
                                                                                             interaction_details,
                                                                                             body,
                                                                                             async_workflow)
        await self.return_sync_async_response(status, response, wdo)

    async def invoke_default_workflow(self, message_id, correlation_id, interaction_details, body, workflow):
        status, response = await workflow.handle_outbound_message(message_id,
                                                                  correlation_id,
                                                                  interaction_details,
                                                                  body,
                                                                  None)
        self._write_response(status, response)

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

    def _retrieve_interaction_details(self, interaction_id):
        interaction_details = self._get_interaction_details(interaction_id)

        if interaction_details is None:
            logger.error('0007', 'Unknown {InteractionId} in request', {'InteractionId': interaction_id})
            raise tornado.web.HTTPError(404, f'Unknown interaction ID: {interaction_id}',
                                        reason=f'Unknown interaction ID: {interaction_id}')
        print(f"deets:{interaction_details}")
        return interaction_details

    def _get_interaction_details(self, interaction_name: str) -> dict:
        return self.config_manager.get_interaction_details(interaction_name)
