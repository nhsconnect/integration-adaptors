"""This module defines the outbound synchronous request handler component."""
import json

import marshmallow
import mhs_common.state.work_description as wd
import mhs_common.workflow as workflow
import tornado.escape
import tornado.locks
import tornado.web
from mhs_common.handler import base_handler
from mhs_common.messages import ebxml_envelope
from utilities import integration_adaptors_logger as log, message_utilities, timing

from outbound.request import request_body_schema

logger = log.IntegrationAdaptorsLogger('MHS_OUTBOUND_HANDLER')


class SynchronousHandler(base_handler.BaseHandler):
    """A Tornado request handler intended to handle incoming HTTP requests from a supplier system."""

    @timing.time_request
    async def post(self):
        """
        ---
        summary: Make a request to the MHS
        description: Make a request to the MHS
        operationId: postMHS
        parameters:
          - name: Interaction-Id
            in: header
            required: true
            schema:
              type: string
            description: ID of the interaction that you want to invoke. e.g. QUPC_IN160101UK05
          - name: sync-async
            in: header
            required: true
            schema:
              type: string
              enum: ["true", "false"]
            description: >-
              If set to true and the interaction ID is for an async interaction
              that supports sync-async, then the HTTP response will be the
              response from Spine, and the response will not be put onto the
              inbound queue.


              If set to false for an async interaction, then the response from
              Spine will be put onto the inbound queue and the HTTP response will
              just acknowledge sending the request successfully to Spine.


              For sync interactions or async interactions that don't support
              sync-async, this header must be set to false.
          - name: from-asid
            in: header
            required: false
            schema:
              type: string
            description: >-
              The ASID of the sending system. This should be the same as the from-asid
              value within the HL7 payload. This header is optional and only
              required/used for interactions that use the sync workflow.
          - name: Message-Id
            in: header
            required: false
            schema:
              type: string
            description: >-
              Message ID of the message to send to Spine. If not sent, the MHS
              generates a random message ID.


              When performing async requests where the response is put on the
              inbound queue, the message ID will be put with the response on the
              queue.
          - name: Correlation-Id
            in: header
            required: false
            schema:
              type: string
            description: >-
              Correlation ID that is used when logging. If not passed, a random
              correlation ID is generated. The idea is that log messages produced
              by the MHS include this correlation ID which allows correlating logs
              relating to a single request together. If the supplier system uses
              it's own correlation ID when producing it's logs, then that should
              be passed in here, so that logs for a single request can be tied
              together across the supplier system and the MHS.


              When performing async requests where the response is put on the
              inbound queue, the correlation ID will be put with the response on the
              queue.


              Note that this correlation ID gets sent to/from Spine.
        responses:
          200:
            description: Successful response from Spine.
            content:
              text/xml: {}
          202:
            description: >-
              Acknowledgement that we successfully sent the message to Spine
              (response will come asynchronously on the inbound queue).
        requestBody:
          required: true
          content:
            application/json:
              schema:
                $ref: '#/definitions/RequestBody'
          description: The HL7 payload (and optional attachments) to be sent to Spine.
        """
        message_id = self._extract_message_id()
        correlation_id = self._extract_correlation_id()
        interaction_id = self._extract_interaction_id()
        sync_async_header = self._extract_sync_async_header()
        from_asid = self._extract_from_asid()
        ods_code = self._extract_ods_code()

        logger.info('0006', 'Outbound POST received. {Request}', {'Request': str(self.request)})

        body = self._parse_body()

        interaction_details = self._retrieve_interaction_details(interaction_id)
        wf = self._extract_default_workflow(interaction_details, interaction_id)
        self._extend_interaction_details(wf, interaction_details)

        interaction_details['ods-code'] = ods_code
        sync_async_interaction_config = self._extract_sync_async_from_interaction_details(interaction_details)

        if self._should_invoke_sync_async_workflow(sync_async_interaction_config, sync_async_header):
            await self._invoke_sync_async(from_asid, message_id, correlation_id, interaction_details, body, wf)
        else:
            await self.invoke_default_workflow(from_asid, message_id, correlation_id, interaction_details, body, wf)

    def _parse_body(self):
        try:
            content_type = self.request.headers['Content-Type']
        except KeyError as e:
            logger.error('0011', 'Missing Content-Type header')
            raise tornado.web.HTTPError(400, 'Missing Content-Type header', reason='Missing Content-Type header') from e
        if content_type != 'application/json':
            logger.error('0012', 'Unsupported content type in request. {ExpectedContentType} {ActualContentType}',
                         {'ExpectedContentType': 'application/json', 'ActualContentType': content_type})
            raise tornado.web.HTTPError(415,
                                        'Unsupported content type. Only application/json request bodies are supported.',
                                        reason='Unsupported content type. Only application/json request bodies are '
                                               'supported.')
        body = self.request.body.decode()
        if not body:
            logger.error('0009', 'Body missing from request')
            raise tornado.web.HTTPError(400, 'Body missing from request', reason='Body missing from request')
        try:
            # Parse the body as JSON and validate it against RequestBodySchema
            parsed_body: request_body_schema.RequestBody = request_body_schema.RequestBodySchema().loads(body)
        except json.JSONDecodeError as e:
            logger.error('0013', 'Invalid JSON request body')
            raise tornado.web.HTTPError(400, 'Invalid JSON request body', reason='Invalid JSON request body') from e
        except marshmallow.ValidationError as e:
            # e.messages is a nested dict of all the validation errors
            validation_errors = str(e.messages)
            logger.error('0014', 'Invalid request. {ValidationErrors}', {'ValidationErrors': validation_errors})
            raise tornado.web.HTTPError(400, f'Invalid request. Validation errors: {validation_errors}',
                                        reason=f'Invalid request. Validation errors: {validation_errors}') from e
        return parsed_body.payload

    def _extract_sync_async_header(self):
        sync_async_header = self.request.headers.get('sync-async', None)
        if not sync_async_header:
            logger.error('0031', 'Failed to parse sync-async header from message')
            raise tornado.web.HTTPError(400, 'Sync-Async header missing', reason='Sync-Async header missing')
        if sync_async_header == 'true':
            return True
        else:
            return False

    def _extract_from_asid(self):
        return self.request.headers.get('from-asid', None)

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
            log.interaction_id.set(interaction_id)
            logger.info('0021', 'Found Interaction-Id in message headers')
        except KeyError as e:
            logger.error('0005', 'Required Interaction-Id header not passed in request')
            raise tornado.web.HTTPError(404, 'Required Interaction-Id header not found',
                                        reason='Required Interaction-Id header not found') from e
        return interaction_id

    def _extract_ods_code(self):
        return self.request.headers.get('ods-code', None)

    def _extend_interaction_details(self, wf, interaction_details):
        if wf.workflow_specific_interaction_details:
            interaction_details.update(wf.workflow_specific_interaction_details)

    def _extract_sync_async_from_interaction_details(self, interaction_details):
        is_sync_async = interaction_details.get('sync_async')
        if is_sync_async is None:
            logger.error('0032', 'Failed to retrieve sync-async flag from interactions.json')
            raise tornado.web.HTTPError(500, f'Failed to parse sync-async flag from interactions.json file',
                                        reason='Failed to find sync-async flag for the interaction within the '
                                               'interactions.json')
        return is_sync_async

    def _should_invoke_sync_async_workflow(self, interaction_config, sync_async_header):
        if interaction_config and sync_async_header:
            return True
        elif (not interaction_config) and sync_async_header:
            logger.error('0033', 'Message header requested sync-async wrap for un-supported sync-async')
            raise tornado.web.HTTPError(400, f'Message header requested sync-async wrap for un-supported sync-async',
                                        reason='Message header requested sync-async wrap for a message pattern '
                                               'that does not support sync-async')
        else:
            return False

    async def _invoke_sync_async(self, from_asid, message_id, correlation_id, interaction_details, body, async_workflow):
        sync_async_workflow: workflow.SyncAsyncWorkflow = self.workflows[workflow.SYNC_ASYNC]
        status, response, wdo = await sync_async_workflow.handle_sync_async_outbound_message(from_asid,
                                                                                             message_id,
                                                                                             correlation_id,
                                                                                             interaction_details,
                                                                                             body,
                                                                                             async_workflow)
        await self.write_response_with_store_updates(status, response, wdo, sync_async_workflow)

    async def write_response_with_store_updates(self, status: int, response: str, wdo: wd.WorkDescription,
                                                wf: workflow.CommonWorkflow):
        try:
            if wdo:
                await wf.set_successful_message_response(wdo)
            self._write_response(status, response)
        except Exception as e:
            logger.error('0015', 'Failed to respond to supplier system {exception}', {'exception': e})
            if wdo:
                await wf.set_failure_message_response(wdo)

    async def invoke_default_workflow(self, from_asid, message_id, correlation_id, interaction_details, body, wf):
            status, response, work_description_response = await wf.handle_outbound_message(from_asid, message_id,
                                                                                           correlation_id,
                                                                                           interaction_details,
                                                                                           body,
                                                                                           None)
            await self.write_response_with_store_updates(status, response, work_description_response, wf)

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

        interaction_details[ebxml_envelope.ACTION] = interaction_id

        return interaction_details
