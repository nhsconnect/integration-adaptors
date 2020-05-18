"""This module defines the outbound synchronous request handler component."""
import json

import marshmallow
import mhs_common.state.work_description as wd
import mhs_common.workflow as workflow
import tornado.escape
import tornado.locks
import tornado.web

from comms.http_headers import HttpHeaders
from utilities import mdc
from mhs_common.handler import base_handler
from mhs_common.messages import ebxml_envelope
from utilities import integration_adaptors_logger as log, message_utilities, timing

from outbound.request import request_body_schema

logger = log.IntegrationAdaptorsLogger(__name__)


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
          - name: wait-for-response
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
          - name: ods-code
            in: header
            required: false
            schema:
              type: string
            description: >-
              ODS Code receiving system. It defaults to Spines ODS Code if not porvided and is primarily used for
              indirect messaging, i.e. forward reliable for example, where the destination system is not Spine. The
              ODS Code is used to lookup the constract properties in SDS.
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
        wait_for_response_header = self._extract_wait_for_response_header()
        from_asid = self._extract_from_asid()
        ods_code = self._extract_ods_code()

        logger.info('Outbound POST received. {Request}', fparams={'Request': str(self.request)})

        body = self._parse_body()

        interaction_details = self._retrieve_interaction_details(interaction_id)
        wf = self._extract_default_workflow(interaction_details, interaction_id)
        self._extend_interaction_details(wf, interaction_details)

        interaction_details['ods-code'] = ods_code
        sync_async_interaction_config = self._extract_sync_async_from_interaction_details(interaction_details)

        if self._should_invoke_sync_async_workflow(sync_async_interaction_config, wait_for_response_header):
            await self._invoke_sync_async(from_asid, message_id, correlation_id, interaction_details, body, wf)
        else:
            await self.invoke_default_workflow(from_asid, message_id, correlation_id, interaction_details, body, wf)

    def _parse_body(self):
        try:
            content_type = self.request.headers[HttpHeaders.CONTENT_TYPE]
        except KeyError as e:
            logger.error('Missing Content-Type header')
            raise tornado.web.HTTPError(400, 'Missing Content-Type header', reason='Missing Content-Type header') from e
        if content_type != 'application/json':
            logger.error('Unsupported content type in request. {ExpectedContentType} {ActualContentType}',
                         fparams={'ExpectedContentType': 'application/json', 'ActualContentType': content_type})
            raise tornado.web.HTTPError(415,
                                        'Unsupported content type. Only application/json request bodies are supported.',
                                        reason='Unsupported content type. Only application/json request bodies are '
                                               'supported.')
        body = self.request.body.decode()
        if not body:
            logger.error('Body missing from request')
            raise tornado.web.HTTPError(400, 'Body missing from request', reason='Body missing from request')
        try:
            # Parse the body as JSON and validate it against RequestBodySchema
            parsed_body: request_body_schema.RequestBody = request_body_schema.RequestBodySchema().loads(body)
        except json.JSONDecodeError as e:
            logger.error('Invalid JSON request body')
            raise tornado.web.HTTPError(400, 'Invalid JSON request body', reason='Invalid JSON request body') from e
        except marshmallow.ValidationError as e:
            # e.messages is a nested dict of all the validation errors
            validation_errors = str(e.messages)
            logger.error('Invalid request. {ValidationErrors}', fparams={'ValidationErrors': validation_errors})
            raise tornado.web.HTTPError(400, f'Invalid request. Validation errors: {validation_errors}',
                                        reason=f'Invalid request. Validation errors: {validation_errors}') from e
        return parsed_body.payload

    def _extract_wait_for_response_header(self):
        wait_for_response_header = self.request.headers.get(HttpHeaders.WAIT_FOR_RESPONSE, None)
        if not wait_for_response_header:
            logger.error('Failed to parse wait-for-response header from message')
            raise tornado.web.HTTPError(400, 'wait-for-response header missing',
                                        reason='wait-for-response header missing')
        if wait_for_response_header.lower() == 'true':
            return True
        elif wait_for_response_header.lower() == 'false':
            return False
        else:
            raise tornado.web.HTTPError(400, 'wait for response should be set to true or false',
                                        reason=f'wait-for-response is set to {wait_for_response_header}')

    def _extract_from_asid(self):
        return self.request.headers.get(HttpHeaders.FROM_ASID, None)

    def _extract_message_id(self):
        message_id = self.request.headers.get(HttpHeaders.MESSAGE_ID, None)
        if not message_id:
            message_id = message_utilities.get_uuid()
            mdc.message_id.set(message_id)
            logger.info("Didn't receive message id in incoming request from supplier, so have generated a new one.")
        else:
            mdc.message_id.set(message_id)
            logger.info('Found message id on incoming request.')
        return message_id

    def _extract_correlation_id(self):
        correlation_id = self.request.headers.get(HttpHeaders.CORRELATION_ID, None)
        if not correlation_id:
            correlation_id = message_utilities.get_uuid()
            mdc.correlation_id.set(correlation_id)
            logger.info("Didn't receive correlation id in incoming request from supplier, so have generated a new one.")
        else:
            mdc.correlation_id.set(correlation_id)
            logger.info('Found correlation id on incoming request.')
        return correlation_id

    def _extract_interaction_id(self):
        try:
            interaction_id = self.request.headers[HttpHeaders.INTERACTION_ID]
            mdc.interaction_id.set(interaction_id)
            logger.info('Found Interaction-Id in message headers')
        except KeyError as e:
            logger.error('Required Interaction-Id header not passed in request')
            raise tornado.web.HTTPError(404, 'Required Interaction-Id header not found',
                                        reason='Required Interaction-Id header not found') from e
        return interaction_id

    def _extract_ods_code(self):
        return self.request.headers.get(HttpHeaders.ODS_CODE, None)

    def _extend_interaction_details(self, wf, interaction_details):
        if wf.workflow_specific_interaction_details:
            interaction_details.update(wf.workflow_specific_interaction_details)

    def _extract_sync_async_from_interaction_details(self, interaction_details):
        is_sync_async = interaction_details.get('sync_async')
        if is_sync_async is None:
            logger.error('Failed to retrieve sync-async flag from interactions.json')
            raise tornado.web.HTTPError(500, f'Failed to parse sync-async flag from interactions.json file',
                                        reason='Failed to find sync-async flag for the interaction within the '
                                               'interactions.json')
        return is_sync_async

    def _should_invoke_sync_async_workflow(self, interaction_config, sync_async_header):
        if interaction_config and sync_async_header:
            return True
        elif (not interaction_config) and sync_async_header:
            logger.error('Message header requested wait-for-response wrap for unsupported sync-async')
            raise tornado.web.HTTPError(400, f'Message header requested wait-for-response wrap for unsupported sync-async',
                                        reason='Message header requested wait-for-response wrap for a message pattern '
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
        await self.write_response_with_store_updates(status, response, wdo, sync_async_workflow, message_id, correlation_id)

    async def write_response_with_store_updates(self, status: int, response: str, wdo: wd.WorkDescription,
                                                wf: workflow.CommonWorkflow,
                                                message_id: str, correlation_id: str):
        try:
            if wdo:
                await wf.set_successful_message_response(wdo)
            self._write_response(status, response, message_id, correlation_id)
        except Exception:
            logger.exception('Failed to respond to supplier system')
            if wdo:
                await wf.set_failure_message_response(wdo)

    async def invoke_default_workflow(self, from_asid, message_id, correlation_id, interaction_details, body, wf):
            status, response, work_description_response = await wf.handle_outbound_message(from_asid, message_id,
                                                                                           correlation_id,
                                                                                           interaction_details,
                                                                                           body,
                                                                                           None)
            await self.write_response_with_store_updates(status, response, work_description_response, wf, message_id, correlation_id)

    def _write_response(self, status: int, message: str, message_id: str, correlation_id: str) -> None:
        """Write the given message to the response.

        :param message: The message to write to the response.
        """
        logger.info('Returning response with {HttpStatus}', fparams={'HttpStatus': status})
        self.set_status(status)
        if 400 <= status:
            content_type = "text/plain"
        else:
            content_type = "text/xml"
        self.set_header(HttpHeaders.CONTENT_TYPE, content_type)
        self.set_header(HttpHeaders.CORRELATION_ID, correlation_id)
        self.set_header(HttpHeaders.MESSAGE_ID, message_id)
        self.write(message)

    def _retrieve_interaction_details(self, interaction_id):
        interaction_details = self._get_interaction_details(interaction_id)

        interaction_details[ebxml_envelope.ACTION] = interaction_id

        return interaction_details
